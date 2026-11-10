"""Wipe every non-admin user and ALL their data (documents, GridFS), keeping only admin
accounts. Stop the backend first. Take a database backup before --apply. Run with:
    python -m app.scripts.wipe_all_except_admins --db <name>                         # dry-run
    python -m app.scripts.wipe_all_except_admins --db <name> --apply --i-have-a-backup # wipe
`--db` must equal the configured MONGO_DB_NAME. Collections and indexes are kept (delete_many only).
Idempotent: after an interruption just re-run. Exit codes: 0 ok, 1 verification failed,
2 --db mismatch, 3 no admin user, 4 --apply without --i-have-a-backup.
"""

import argparse
import asyncio
import sys
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.core.config import settings

DATA_COLLECTIONS = (
    "documents",
    "corrections",
    "auditlogs",
    "orphanedfiles",
    "settings",
    "passwordresetrequests",
    "chatmessages",
    "chatattachments",
    "chatfileorphans",
)
GRIDFS_COLLECTIONS = ("fs.files", "fs.chunks", "chatfs.files", "chatfs.chunks")
NON_ADMIN = {"role": {"$ne": "admin"}}


async def _snapshot(db: AsyncIOMotorDatabase) -> dict[str, Any]:
    agg = (
        await db["fs.files"]
        .aggregate([{"$group": {"_id": None, "n": {"$sum": "$length"}}}])
        .to_list(1)
    )
    return {
        "admins": sorted(
            await db.users.find({"role": "admin"}).to_list(None), key=lambda a: a["_id"]
        ),
        "non_admin": await db.users.count_documents(NON_ADMIN),
        "counts": {n: await db[n].count_documents({}) for n in DATA_COLLECTIONS},
        "gridfs_files": await db["fs.files"].count_documents({}),
        "gridfs_chunks": await db["fs.chunks"].count_documents({}),
        "gridfs_bytes": agg[0]["n"] if agg else 0,
        "chatfs_files": await db["chatfs.files"].count_documents({}),
        "chatfs_chunks": await db["chatfs.chunks"].count_documents({}),
    }


def _print_table(s: dict[str, Any], applied: bool) -> None:
    verb = "deleted" if applied else "to delete"
    print(f"\n  {'collection':<22}{verb:>12}{'kept':>8}")
    print(f"  {'users':<22}{s['non_admin']:>12}{len(s['admins']):>8}   (non-admin / admin)")
    for name, n in s["counts"].items():
        print(f"  {name:<22}{n:>12}{0:>8}")
    print(
        f"  GridFS: {s['gridfs_files']} files, {s['gridfs_chunks']} chunks, "
        f"{s['gridfs_bytes']} bytes {verb}"
    )
    print(f"  Chat GridFS: {s['chatfs_files']} files, {s['chatfs_chunks']} chunks {verb}")
    print(f"  Admin accounts that stay ({len(s['admins'])}):")
    for a in s["admins"]:
        print(f"    {a.get('email')}")


async def _wipe(db: AsyncIOMotorDatabase) -> None:
    """Order: non-admin users (kills their tokens at once), data, GridFS."""
    await db.users.delete_many(NON_ADMIN)
    for name in DATA_COLLECTIONS:
        await db[name].delete_many({})
    for name in GRIDFS_COLLECTIONS:  # files first, then chunks; a rerun clears any orphan chunks
        await db[name].delete_many({})


async def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="wipe_all_except_admins")
    parser.add_argument("--db", required=True, help="database name; must match MONGO_DB_NAME")
    parser.add_argument("--apply", action="store_true", help="delete (default: dry-run)")
    parser.add_argument("--i-have-a-backup", action="store_true", dest="backup")
    args = parser.parse_args(argv)

    if args.db != settings.mongo_db_name:
        print(
            f"REFUSED: --db {args.db!r} does not match the configured database "
            f"{settings.mongo_db_name!r}. Nothing changed."
        )
        return 2
    if args.apply and not args.backup:
        print("REFUSED: --apply requires --i-have-a-backup (back up the database first).")
        return 4

    print("STOP THE BACKEND FIRST (it must not be writing while this runs).")
    print(f"Database: {args.db}  mode: {'APPLY' if args.apply else 'dry-run'}")
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        settings.mongo_uri, serverSelectionTimeoutMS=10000, tz_aware=True
    )
    try:
        db = client[args.db]
        try:
            await client.admin.command("ping")
            before = await _snapshot(db)
        except PyMongoError as exc:
            print(f"ERROR: could not talk to MongoDB ({type(exc).__name__}). Nothing changed.")
            return 1
        if not before["admins"]:
            print(
                "REFUSED: no admin user exists - the wipe would lock everyone out. "
                "Run `python -m app.scripts.seed_admin` first. Nothing changed."
            )
            return 3
        _print_table(before, applied=False)
        if not args.apply:
            print("\nDry-run only - nothing changed. Re-run with --apply --i-have-a-backup.")
            return 0

        try:
            await _wipe(db)
            after = await _snapshot(db)
        except PyMongoError as exc:
            print(f"FAIL: database error mid-wipe ({type(exc).__name__}). Re-run to finish.")
            return 1
        problems = []
        if after["admins"] != before["admins"]:
            problems.append("admin accounts changed or missing")
        problems += [f"{n} still has {c} rows" for n, c in after["counts"].items() if c]
        if after["non_admin"]:
            problems.append(f"{after['non_admin']} non-admin users remain")
        if after["gridfs_files"] or after["gridfs_chunks"]:
            problems.append("GridFS is not empty")
        if after["chatfs_files"] or after["chatfs_chunks"]:
            problems.append("Chat GridFS is not empty")

        print("\n=== RESULT ===")
        if problems:
            print("FAIL")
            for p in problems:
                print(f"  - {p}")
            return 1
        print(f"PASS - only {len(before['admins'])} admin account(s) remain; all else is empty.")
        print("Restart the backend (clears in-memory login rate limits).")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(run(sys.argv[1:])))
