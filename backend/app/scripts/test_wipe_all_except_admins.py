"""Contract tests for scripts/wipe_all_except_admins.py (written from the spec).
SAFETY: every DB name used here must end in "_test" (see _guard)."""

import ast
import asyncio
import io
import os
import re
import subprocess
import sys
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from PIL import Image

from app.core.config import settings
from app.core.database import _ensure_indexes
from app.features.ocr import extraction as ex
from app.features.ocr import paddle_runner, pipeline
from app.scripts import wipe_all_except_admins as wipe

SUB_DB = "ackn_wipe_check_test"
BACKEND = Path(__file__).resolve().parents[2]
PW_HASH_MARK = "$2b$"
FILE_MARK = b"SECRET-FILE-CONTENT-7731"
NON_ADMIN_DOMAIN = "nonadmin-secret.example"
ROW_COLLECTIONS = [
    "documents",
    "corrections",
    "auditlogs",
    "orphanedfiles",
    "settings",
    "chatmessages",
]
COUNTS = {
    "chatmessages": 9,
    "documents": 3,
    "corrections": 4,
    "auditlogs": 6,
    "orphanedfiles": 7,
    "settings": 8,
}
INDEXED = ["documents", "users", "settings", "orphanedfiles"]


def _guard(name: str) -> str:
    assert name.endswith("_test"), f"refusing non-test DB name {name!r}"
    return name


async def _run(name: str, *flags: str) -> int:
    return await wipe.run(["--db", _guard(name), *flags])


# ---------- seeding / snapshots ----------


async def _seed(db: Any, make_user: Any) -> dict[str, Any]:
    _guard(db.name)
    await _ensure_indexes(db)
    a1 = await make_user(role="admin", email="boss1@looptest.local")
    a2 = await make_user(role="admin", email="boss2@looptest.local")
    await db.users.update_one({"_id": a1.id}, {"$set": {"tokenVersion": 7}})
    users = [
        await make_user(email=f"ok@{NON_ADMIN_DOMAIN}"),
        await make_user(email=f"wait@{NON_ADMIN_DOMAIN}"),
        await make_user(email=f"no@{NON_ADMIN_DOMAIN}"),
    ]
    await db.users.insert_one(  # legacy user with no role/status at all
        {"username": "legacy", "email": f"old@{NON_ADMIN_DOMAIN}", "tokenVersion": 0}
    )
    now = datetime.now(UTC)
    for name in ROW_COLLECTIONS:
        rows = []
        for n in range(COUNTS[name]):
            row: dict[str, Any] = {"userId": users[0].id, "n": n, "createdAt": now}
            if name == "orphanedfiles":
                row["gridFsFileId"] = ObjectId()
            if name == "settings":
                row["key"] = f"k{n}"
            rows.append(row)
        await db[name].insert_many(rows)
    bucket = AsyncIOMotorGridFSBucket(db)
    for i in range(3):
        await bucket.upload_from_stream(f"f{i}.png", FILE_MARK * (i + 1))
    return {"admins": [a1, a2], "users": users}


async def _snapshot(db: Any) -> dict[str, list[dict[str, Any]]]:
    out = {}
    for name in sorted(await db.list_collection_names()):
        out[name] = await db[name].find({}).sort("_id", 1).to_list(None)
    return out


async def _indexes(db: Any) -> dict[str, set[str]]:
    return {c: {i["name"] async for i in db[c].list_indexes()} for c in INDEXED}


def _line(out: str, name: str) -> str:
    return next(ln for ln in out.splitlines() if name in ln.split())


# ---------- 1. dry run ----------


async def test_dry_run_changes_nothing_and_prints_counts(
    db: Any, make_user: Any, capsys: Any
) -> None:
    s = await _seed(db, make_user)
    before = await _snapshot(db)
    capsys.readouterr()
    assert await _run(db.name) == 0
    assert await _snapshot(db) == before
    out = capsys.readouterr().out
    for name, n in {**COUNTS, "users": 4}.items():
        assert re.search(rf"(?<!\d){n}(?!\d)", _line(out, name)), (name, _line(out, name))
    for admin in s["admins"]:
        assert admin.email in out


# ---------- 2. apply ----------


async def test_apply_keeps_admins_wipes_rest(db: Any, make_user: Any) -> None:
    s = await _seed(db, make_user)
    admins_before = await db.users.find({"role": "admin"}).sort("_id", 1).to_list(None)
    idx_before = await _indexes(db)
    assert await _run(db.name, "--apply", "--i-have-a-backup") == 0
    assert await db.users.find({"role": "admin"}).sort("_id", 1).to_list(None) == admins_before
    assert await db.users.count_documents({}) == 2
    for name in ROW_COLLECTIONS + ["fs.files", "fs.chunks"]:
        assert await db[name].count_documents({}) == 0, name
    assert await _indexes(db) == idx_before
    assert "email_1" in idx_before["users"]
    dup = {"username": "dup", "email": s["admins"][0].email, "role": "user"}
    with pytest.raises(Exception, match="E11000"):
        await db.users.insert_one(dup)


# ---------- 3. refusals ----------


async def _assert_refused(db: Any, code: int, name: str, *flags: str) -> None:
    before = await _snapshot(db)
    assert await _run(name, *flags) == code
    assert await _snapshot(db) == before


async def test_apply_without_backup_flag_refused(db: Any, make_user: Any) -> None:
    await _seed(db, make_user)
    await _assert_refused(db, 4, db.name, "--apply")


async def test_wrong_db_refused(db: Any, make_user: Any) -> None:
    await _seed(db, make_user)
    await _assert_refused(db, 2, "ackn_some_other_test", "--apply", "--i-have-a-backup")


@pytest.mark.parametrize("variant", ["none", "role_user", "no_role_field"])
async def test_no_admin_refused(db: Any, make_user: Any, variant: str) -> None:
    await _seed(db, make_user)
    await db.users.delete_many({"role": "admin"})
    if variant == "role_user":
        await db.users.insert_one({"username": "fake", "email": "f@x.example", "role": "user"})
    elif variant == "no_role_field":
        await db.users.insert_one({"username": "fake", "email": "f@x.example"})
    await _assert_refused(db, 3, db.name, "--apply", "--i-have-a-backup")
    await _assert_refused(db, 3, db.name)  # dry run refuses too


# ---------- 4. idempotent / orphan chunks ----------


async def test_second_run_deletes_nothing_and_orphan_chunks_cleaned(
    db: Any, make_user: Any, capsys: Any
) -> None:
    await _seed(db, make_user)
    flags = ("--apply", "--i-have-a-backup")
    assert await _run(db.name, *flags) == 0
    await db["fs.chunks"].insert_one({"files_id": ObjectId(), "n": 0, "data": b"orphan"})
    assert await _run(db.name, *flags) == 0
    assert await db["fs.chunks"].count_documents({}) == 0
    assert await db.users.count_documents({}) == 2
    capsys.readouterr()
    assert await _run(db.name, *flags) == 0
    assert await _run(db.name) == 0
    out = capsys.readouterr().out
    for name in ROW_COLLECTIONS:
        assert not re.search(r"[1-9]", _line(out, name).replace(name, "")), _line(out, name)


# ---------- 5. DB-name safety ----------


def test_no_non_test_db_name_in_this_file() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.fullmatch(r"ackn\w*", node.value):
                assert node.value.endswith("_test"), node.value
    assert SUB_DB.endswith("_test") and settings.mongo_db_name.endswith("_test")


# ---------- 6. nothing sensitive in output ----------


async def test_output_has_no_secrets(db: Any, make_user: Any, capsys: Any) -> None:
    s = await _seed(db, make_user)
    hashes = [u["passwordHash"] async for u in db.users.find({"passwordHash": {"$exists": True}})]
    tokens = [a._token for a in s["admins"] + s["users"]]
    capsys.readouterr()
    await _run(db.name)
    await _run(db.name, "--apply")  # refusal path
    await _run(db.name, "--apply", "--i-have-a-backup")
    cap = capsys.readouterr()
    out = cap.out + cap.err
    assert hashes and PW_HASH_MARK not in out
    for secret in hashes + tokens + [FILE_MARK.decode(), NON_ADMIN_DOMAIN]:
        assert secret not in out
    for u in s["users"]:
        assert u.email not in out and u.password not in out


# ---------- subprocess (real CLI, throwaway DB) ----------


@pytest_asyncio.fixture
async def sub_db(real_motor_client: Any) -> AsyncIterator[Any]:
    client: Any = real_motor_client(settings.mongo_uri)  # the subprocess uses the real server
    database = client[_guard(SUB_DB)]
    try:
        yield database
    finally:
        assert database.name == SUB_DB
        for name in await database.list_collection_names():
            await database[name].delete_many({})
        client.close()


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "MONGO_DB_NAME": _guard(SUB_DB)}
    return subprocess.run(
        [sys.executable, "-m", "app.scripts.wipe_all_except_admins", *args],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.mark.live  # spawns a separate process, which cannot see the in-process fake DB
async def test_cli_subprocess(sub_db: Any) -> None:
    await sub_db.users.insert_many(
        [
            {"username": "adm", "email": "adm@looptest.local", "role": "admin"},
            {"username": "usr", "email": f"u@{NON_ADMIN_DOMAIN}", "role": "user"},
        ]
    )
    await sub_db.documents.insert_one({"n": 1})

    assert _cli("--db", "ackn_other_test").returncode == 2
    assert _cli("--db", SUB_DB, "--apply").returncode == 4
    dry = _cli("--db", SUB_DB)
    assert dry.returncode == 0 and NON_ADMIN_DOMAIN not in dry.stdout + dry.stderr
    assert await sub_db.documents.count_documents({}) == 1
    done = _cli("--db", SUB_DB, "--apply", "--i-have-a-backup")
    assert done.returncode == 0, done.stdout + done.stderr
    assert await sub_db.documents.count_documents({}) == 0
    assert [u["username"] async for u in sub_db.users.find({})] == ["adm"]


# ---------- 7. app works after the wipe ----------


async def test_app_flow_after_wipe(
    db: Any,
    client: Any,
    make_user: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s = await _seed(db, make_user)
    assert await _run(db.name, "--apply", "--i-have-a-backup") == 0

    pipeline._reset_slot_for_tests()
    paddle_runner._reset_engine_for_tests()
    monkeypatch.setattr(pipeline, "run_ocr", lambda _p, **_k: "OCR TEXT")
    monkeypatch.setattr(pipeline, "classify_page_orientation", lambda _b: (0, 1.0))

    async def ai(_text: str, **_k: Any) -> dict[str, Any]:
        return dict(
            ex.build_extraction_result({"receiptNumber": "TR/2526/000123", "date": "05/10/2026"})
        )

    monkeypatch.setattr(pipeline, "extract_header", ai)

    admin = s["admins"][0]
    login = await client.post(
        "/api/auth/login", json={"email": admin.email, "password": admin.password}
    )
    assert login.status_code == 200

    creds = {"username": "freshie", "email": "fresh@looptest.local", "password": "Xq7!mZv#4Lp2"}
    sg = await client.post("/api/auth/signup", json=creds)
    assert sg.status_code == 201, sg.text
    login_body = {"email": creds["email"], "password": creds["password"]}
    tok = await client.post("/api/auth/login", json=login_body)
    assert tok.status_code == 200
    h = {"Authorization": f"Bearer {tok.json()['token']}"}

    buf = io.BytesIO()
    Image.new("RGB", (200, 200), "white").save(buf, format="PNG")
    up = await client.post(
        "/api/documents/upload",
        headers=h,
        files={"document": ("a.png", io.BytesIO(buf.getvalue()), "image/png")},
    )
    assert up.status_code == 201, up.text
    doc_id = ObjectId(up.json()["document"]["_id"])
    doc: dict[str, Any] | None = None
    for _ in range(100):
        doc = await db.documents.find_one({"_id": doc_id})
        if doc and doc.get("uploadStatus") == "processed":
            break
        await asyncio.sleep(0.05)
    else:
        raise AssertionError(f"document never processed: {doc}")
    assert doc["receiptNumber"] == "TR/2526/000123"
    pipeline._reset_slot_for_tests()
