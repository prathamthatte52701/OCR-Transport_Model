"""wipe_all_except_admins also clears the passwordresetrequests collection.
SAFETY: only the "_test" database from the db fixture is used."""

from datetime import UTC, datetime
from typing import Any

from app.scripts import wipe_all_except_admins as wipe


async def _seed(db: Any, make_user: Any, n: int = 3) -> Any:
    assert db.name.endswith("_test")
    admin = await make_user(role="admin")
    user = await make_user()
    now = datetime.now(UTC)
    await db.passwordresetrequests.insert_many(
        [
            {
                "userId": user.id,
                "email": user.email,
                "username": user.username,
                "note": f"n{i}",
                "status": "done" if i else "open",
                "resolution": None,
                "createdAt": now,
                "updatedAt": now,
                "resolvedAt": None,
                "resolvedBy": None,
            }
            for i in range(n)
        ]
    )
    return admin


async def test_collection_is_listed_in_data_collections() -> None:
    assert "passwordresetrequests" in wipe.DATA_COLLECTIONS


async def test_dry_run_keeps_requests_and_prints_count(
    db: Any, make_user: Any, capsys: Any
) -> None:
    await _seed(db, make_user, 3)
    capsys.readouterr()
    assert await wipe.run(["--db", db.name]) == 0
    assert await db.passwordresetrequests.count_documents({}) == 3
    out = capsys.readouterr().out
    line = next(ln for ln in out.splitlines() if "passwordresetrequests" in ln.split())
    assert "3" in line


async def test_apply_wipes_requests_keeps_admin(db: Any, make_user: Any) -> None:
    admin = await _seed(db, make_user, 3)
    code = await wipe.run(["--db", db.name, "--apply", "--i-have-a-backup"])
    assert code == 0
    assert await db.passwordresetrequests.count_documents({}) == 0
    assert await db.users.count_documents({}) == 1
    assert (await db.users.find_one({"_id": admin.id})) is not None


async def test_refused_apply_leaves_requests(db: Any, make_user: Any) -> None:
    await _seed(db, make_user, 2)
    assert await wipe.run(["--db", db.name, "--apply"]) == 4
    assert await db.passwordresetrequests.count_documents({}) == 2
