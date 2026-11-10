"""ONE-OFF, LOCAL-ONLY: wipe every user and all data from the ACKN database, keeping only the
accounts whose role is "admin". Never commit this file (it is listed in .git/info/exclude).

    python -m app.scripts.reset_database --db <name>                 # dry-run (default)
    python -m app.scripts.reset_database --db <name> --apply         # backup, confirm, delete
    python -m app.scripts.reset_database --db <name> --apply --keep-exports

--db must equal settings.mongo_db_name. Idempotent: safe to re-run after an interruption.
"""

import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bson import json_util
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.features.excel import service as excel_service

BACKEND_DIR = Path(__file__).resolve().parents[2]

# Deletion order after the non-admin users (indexes are kept: delete_many, not drop).
DATA_COLLECTIONS = [
    "documents",
    "workbooks",
    "exportedrows",
    "auditlogs",
    "orphanedfiles",
    "settings",
    "corrections",
    "chatmessages",
]
BACKUP_COLLECTIONS = ["users", *DATA_COLLECTIONS]
GRIDFS_COLLECTIONS = ["fs.files", "fs.chunks"]
EXPORT_SUFFIXES = (".xlsx", ".lock")  # also covers .tmp{pid}.xlsx


def _is_export_file(name: str) -> bool:
    return name.lower().endswith(EXPORT_SUFFIXES)


def _list_export_files(exports_dir: Path) -> tuple[list[Path], list[str]]:
    """(deletable files, refused entries). Only regular files directly inside the folder are
    deletable; symlinks and anything resolving outside the folder are refused, never followed."""
    if not exports_dir.exists():
        return [], []
    if exports_dir.is_symlink():
        return [], [f"{exports_dir} (exports folder itself is a symlink)"]
    root = exports_dir.resolve()
    files: list[Path] = []
    refused: list[str] = []
    for entry in os.scandir(root):
        if not _is_export_file(entry.name):
            continue  # .gitkeep and anything else stays
        path = Path(entry.path)
        if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
            refused.append(f"{entry.name} (symlink or not a regular file)")
        elif path.resolve().parent != root:
            refused.append(f"{entry.name} (resolves outside the exports folder)")
        else:
            files.append(path)
    return files, refused


async def _summary(db: AsyncIOMotorDatabase, exports_dir: Path) -> dict[str, Any]:
    counts = {name: await db[name].count_documents({}) for name in BACKUP_COLLECTIONS}
    gridfs_files = await db["fs.files"].count_documents({})
    agg = (
        await db["fs.files"]
        .aggregate([{"$group": {"_id": None, "n": {"$sum": "$length"}}}])
        .to_list(1)
    )
    admins = await db.users.find({"role": "admin"}).to_list(None)
    files, refused = _list_export_files(exports_dir)
    return {
        "counts": counts,
        "gridfs_files": gridfs_files,
        "gridfs_chunks": await db["fs.chunks"].count_documents({}),
        "gridfs_bytes": agg[0]["n"] if agg else 0,
        "admins": admins,
        "non_admin_users": await db.users.count_documents({"role": {"$ne": "admin"}}),
        "export_files": files,
        "export_refused": refused,
    }


def _print_summary(db_name: str, s: dict[str, Any], exports_dir: Path) -> None:
    print(f"\nDatabase: {db_name}")
    for name, n in s["counts"].items():
        print(f"  {name:<14} {n}")
    print(f"  GridFS: {s['gridfs_files']} files, {s['gridfs_bytes']} bytes")
    print(f"  Export files on disk ({exports_dir}): {len(s['export_files'])}")
    for r in s["export_refused"]:
        print(f"    REFUSED: {r}")
    print(f"Admin accounts KEPT ({len(s['admins'])}):")
    for a in s["admins"]:
        print(
            f"  {a.get('email')}  username={a.get('username')}  role={a.get('role')}  "
            f"status={a.get('status', '(none)')}"
        )
    print(f"Non-admin users to be DELETED: {s['non_admin_users']}")


async def _write_backup(db: AsyncIOMotorDatabase, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=False)
    for name in BACKUP_COLLECTIONS:
        expected = await db[name].count_documents({})
        written = 0
        with open(backup_dir / f"{name}.json", "w", encoding="utf-8") as f:
            f.write("[\n")
            async for doc in db[name].find({}):
                if written:
                    f.write(",\n")
                f.write(json_util.dumps(doc))
                written += 1
            f.write("\n]\n")
            f.flush()
            os.fsync(f.fileno())
        if written < expected:  # more is fine (a live app may have inserted meanwhile)
            raise RuntimeError(f"{name}: wrote {written} of {expected} records")
        print(f"  backed up {name}: {written}")


async def _wipe(db: AsyncIOMotorDatabase, keep_exports: bool, files: list[Path]) -> None:
    await db.users.delete_many({"role": {"$ne": "admin"}})  # invalidates their tokens at once
    for name in DATA_COLLECTIONS:
        await db[name].delete_many({})
    for name in GRIDFS_COLLECTIONS:
        await db.drop_collection(name)
    if not keep_exports:
        for path in files:
            path.unlink(missing_ok=True)


async def run(
    argv: list[str],
    *,
    exports_dir: Path | None = None,
    backup_root: Path | None = None,
) -> int:
    parser = argparse.ArgumentParser(prog="reset_database")
    parser.add_argument("--db", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep-exports", action="store_true")
    args = parser.parse_args(argv)
    exports_dir = exports_dir or excel_service.EXPORT_DIR
    backup_root = backup_root or BACKEND_DIR

    if args.db != settings.mongo_db_name:
        print(
            f"ABORT: --db {args.db!r} does not match the configured database "
            f"{settings.mongo_db_name!r}. Nothing changed."
        )
        return 2

    client: AsyncIOMotorClient = AsyncIOMotorClient(
        settings.mongo_uri, serverSelectionTimeoutMS=10000, tz_aware=True
    )
    try:
        db = client[args.db]
        await client.admin.command("ping")
        s = await _summary(db, exports_dir)
        _print_summary(args.db, s, exports_dir)

        if not s["admins"]:
            print(
                "\nABORT: there are no admin accounts - this would lock everyone out. "
                "Nothing changed."
            )
            return 3
        if not args.apply:
            print("\nDRY-RUN only - nothing was changed. Add --apply to wipe.")
            return 0

        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = backup_root / f"backup_{args.db}_{stamp}"
        print(f"\nWriting backup to {backup_dir} ...")
        try:
            await _write_backup(db, backup_dir)
        except Exception as exc:  # noqa: BLE001
            print(f"ABORT: backup failed ({exc}). Nothing was deleted.")
            return 4
        print(
            "Backup complete. NOTE: GridFS file contents (the original PDFs/images) are NOT in "
            "this backup. The backup contains password hashes and customer data - store it "
            "safely and delete it when no longer needed."
        )

        phrase = f"DELETE {args.db}"
        if input(f"\nType exactly `{phrase}` to wipe everything except admins: ") != phrase:
            print("ABORT: confirmation did not match. Nothing was deleted.")
            return 5

        admins_before = {a["_id"]: a for a in s["admins"]}
        await _wipe(db, args.keep_exports, s["export_files"])

        after = await _summary(db, exports_dir)
        problems: list[str] = []
        for name in DATA_COLLECTIONS:
            if after["counts"][name]:
                problems.append(f"{name} still has {after['counts'][name]} documents")
        if after["counts"]["users"] != len(admins_before):
            problems.append(f"users is {after['counts']['users']}, expected {len(admins_before)}")
        admins_after = {a["_id"]: a for a in after["admins"]}
        if admins_after != admins_before:
            problems.append("admin accounts differ from before")
        if after["gridfs_files"] or after["gridfs_chunks"]:
            problems.append("GridFS is not empty")
        if not args.keep_exports and (after["export_files"] or after["export_refused"]):
            problems.append(
                f"export files remain: {len(after['export_files'])} deletable, "
                f"{len(after['export_refused'])} refused"
            )

        print("\n=== RESULT ===")
        if problems:
            print("FAIL")
            for p in problems:
                print(f"  - {p}")
            return 1
        print(
            f"PASS - only the {len(admins_before)} admin account(s) remain; "
            "everything else is empty."
        )
        print(
            "Next: restart the backend so in-memory state (login rate limits) is cleared. "
            "If the backend runs on a separate server, clean its export files there too. "
            f"The backup folder {backup_dir} holds password hashes and customer data - "
            "keep it safe and delete it later."
        )
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(run(sys.argv[1:])))
