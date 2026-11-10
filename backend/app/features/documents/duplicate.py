"""Duplicate warning (spec section 7 item 8 / section 15): same operator + receiptNumber +
date already exists for this user. WARN only, never blocks. Stored as a boolean `isDuplicate`
flag (not recomputed on every read like the other warnings) because it needs a database
query - computed once right after a successful extraction, and refreshed whenever a
correction changes one of the three fields it depends on."""

from typing import Any


async def check_duplicate(db: Any, user_id: Any, doc_id: Any, doc: dict) -> bool:
    """True when another (non-deleted) document owned by the same user shares the same
    operatorName + receiptNumber + date. Blank fields never count as a match (an empty
    receiptNumber on two documents is not a duplicate - it's two documents missing the
    same field)."""
    receipt_number = doc.get("receiptNumber")
    date = doc.get("date")
    operator_name = doc.get("operatorName")
    if not receipt_number or not date or not operator_name:
        return False
    existing = await db.documents.find_one(
        {
            "_id": {"$ne": doc_id},
            "userId": user_id,
            "isDeleted": {"$ne": True},
            "operatorName": operator_name,
            "receiptNumber": receipt_number,
            "date": date,
        },
        {"_id": 1},
    )
    return existing is not None


async def refresh_duplicate_flag(db: Any, user_id: Any, doc_id: Any, doc: dict) -> bool:
    """Recomputes and writes `isDuplicate` for this one document. Returns the new value."""
    is_duplicate = await check_duplicate(db, user_id, doc_id, doc)
    await db.documents.update_one({"_id": doc_id}, {"$set": {"isDuplicate": is_duplicate}})
    return is_duplicate
