"""Duplicate warning (spec section 7 item 8 / section 15): same operator + receiptNumber +
date already exists for this user. WARN only, never blocks. Stored as a boolean `isDuplicate`
flag (not recomputed on every read like the other warnings) because it needs a database
query - computed once right after a successful extraction, and refreshed whenever a
correction changes one of the three fields it depends on."""

import re
from typing import Any


def _exact_ci_regex(value: str) -> re.Pattern:
    """Case-insensitive, whitespace-collapsed exact match: trims each side, collapses any run
    of internal whitespace to match any run of whitespace in the stored value (I6 - "BABA
    TRAVELS" vs "Baba Travels", "P98506" vs "p98506 " must be treated as the same value)."""
    parts = [re.escape(p) for p in value.strip().split()]
    return re.compile(r"^\s*" + r"\s+".join(parts) + r"\s*$", re.IGNORECASE)


async def check_duplicate(db: Any, user_id: Any, doc_id: Any, doc: dict) -> bool:
    """True when another (non-deleted) document owned by the same user shares the same
    operatorName + receiptNumber + date (operatorName/receiptNumber compared case-insensitively
    and whitespace-normalised; date is already a normalised DD/MM/YYYY string). Blank fields
    never count as a match (an empty receiptNumber on two documents is not a duplicate - it's
    two documents missing the same field)."""
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
            "operatorName": _exact_ci_regex(operator_name),
            "receiptNumber": _exact_ci_regex(receipt_number),
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


async def refresh_peers(db: Any, user_id: Any, exclude_id: Any, *keys: dict) -> None:
    """Re-checks isDuplicate on every OTHER non-deleted doc of this owner that shares any of
    the given operator+receiptNumber+date keys (a doc's old and new key after an edit, or its
    key after a delete). One targeted query per key; blank keys are skipped."""
    seen: set = set()
    for key in keys:
        if not (key.get("operatorName") and key.get("receiptNumber") and key.get("date")):
            continue
        cursor = db.documents.find(
            {
                "_id": {"$ne": exclude_id},
                "userId": user_id,
                "isDeleted": {"$ne": True},
                "operatorName": _exact_ci_regex(key["operatorName"]),
                "receiptNumber": _exact_ci_regex(key["receiptNumber"]),
                "date": key["date"],
            }
        )
        async for peer in cursor:
            if peer["_id"] not in seen:
                seen.add(peer["_id"])
                await refresh_duplicate_flag(db, user_id, peer["_id"], peer)
