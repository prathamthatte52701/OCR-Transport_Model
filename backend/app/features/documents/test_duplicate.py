"""Duplicate-flag tests: same operator+receiptNumber+date within one user's documents."""

from datetime import UTC, datetime
from typing import Any

from app.features.documents.duplicate import check_duplicate, refresh_duplicate_flag


async def _insert(db: Any, user_id: Any, **fields: Any) -> Any:
    now = datetime.now(UTC)
    base = {
        "userId": user_id,
        "operatorName": "Baba Travels",
        "receiptNumber": "P98506",
        "date": "25/02/2025",
        "isDeleted": False,
        "createdAt": now,
        "updatedAt": now,
    }
    base.update(fields)
    res = await db.documents.insert_one(base)
    return res.inserted_id


async def test_no_duplicate_when_alone(db: Any, make_user: Any) -> None:
    u = await make_user()
    doc_id = await _insert(db, u.id)
    doc = await db.documents.find_one({"_id": doc_id})
    assert await check_duplicate(db, u.id, doc_id, doc) is False


async def test_duplicate_detected_same_operator_receipt_date(db: Any, make_user: Any) -> None:
    u = await make_user()
    await _insert(db, u.id)
    doc_id = await _insert(db, u.id)
    doc = await db.documents.find_one({"_id": doc_id})
    assert await check_duplicate(db, u.id, doc_id, doc) is True


async def test_not_a_duplicate_across_different_users(db: Any, make_user: Any) -> None:
    u1, u2 = await make_user(), await make_user()
    await _insert(db, u1.id)
    doc_id = await _insert(db, u2.id)
    doc = await db.documents.find_one({"_id": doc_id})
    assert await check_duplicate(db, u2.id, doc_id, doc) is False


async def test_blank_fields_never_count_as_duplicate(db: Any, make_user: Any) -> None:
    u = await make_user()
    await _insert(db, u.id, receiptNumber="")
    doc_id = await _insert(db, u.id, receiptNumber="")
    doc = await db.documents.find_one({"_id": doc_id})
    assert await check_duplicate(db, u.id, doc_id, doc) is False


async def test_deleted_document_not_counted(db: Any, make_user: Any) -> None:
    u = await make_user()
    await _insert(db, u.id, isDeleted=True)
    doc_id = await _insert(db, u.id)
    doc = await db.documents.find_one({"_id": doc_id})
    assert await check_duplicate(db, u.id, doc_id, doc) is False


async def test_refresh_duplicate_flag_writes_field(db: Any, make_user: Any) -> None:
    u = await make_user()
    await _insert(db, u.id)
    doc_id = await _insert(db, u.id)
    doc = await db.documents.find_one({"_id": doc_id})
    assert await refresh_duplicate_flag(db, u.id, doc_id, doc) is True
    updated = await db.documents.find_one({"_id": doc_id})
    assert updated["isDuplicate"] is True
