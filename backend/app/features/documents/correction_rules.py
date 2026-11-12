"""The ONE set of rules for a manual field correction, shared by the user route
(documents/router.py) and the admin route (admin/router.py) so they cannot drift."""

import re
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException

from app.features.documents.correction import correction_set_fields
from app.features.documents.duplicate import refresh_duplicate_flag
from app.features.ocr.extraction import (
    AMOUNT_RE,
    EXTRACTION_VALUE_FIELDS,
    GSTIN_RE,
    PHONE_RE,
    normalize_date_to_ddmmyyyy,
)

EDITABLE_FIELDS = set(EXTRACTION_VALUE_FIELDS)
_AMOUNT_FIELDS = {"packageCount", "freight", "deliveryCharge", "demurrage", "sgst", "cgst", "igst", "totalAmount"}
_GSTIN_FIELDS = {"operatorGstin", "consignorGstin", "consigneeGstin"}
_PHONE_FIELDS = {"consignorPhone", "consigneePhone"}
# Plain text (names, places, addresses, descriptions, remarks): blocks control characters,
# HTML/script tags and "=HYPERLINK(...)"-style formula injection; everything else - including
# punctuation in an address or a name with an apostrophe - is allowed. Max 300 chars.
SAFE_TEXT_RE = re.compile(r"^[^\x00-\x08\x0b\x0c\x0e-\x1f<>]{1,300}$")
CHANGED_MSG = "This document changed while you were editing. Please reload and try again."


def check_request(field: str, value: str | None) -> None:
    """Checks that need no document (run before the lookup, so they win over a 404)."""
    if field not in EDITABLE_FIELDS:
        raise HTTPException(status_code=400, detail="That field cannot be edited.")
    if value is None:
        raise HTTPException(status_code=400, detail="Please enter a value before saving.")


def validate_correction(doc: dict, field: str, raw_value: str) -> str:
    """Returns the cleaned value to store, or raises 409 / 400."""
    # A document still mid-OCR can flip to 'processed' right after it is read and silently
    # overwrite a correction made in that window - block until processing has finished.
    if doc["uploadStatus"] not in ("processed", "failed"):
        raise HTTPException(
            status_code=409,
            detail=(
                "This document is still being processed. "
                "Please wait for it to finish before editing."
            ),
        )
    value = raw_value.strip()
    if not value:
        return ""  # empty (or whitespace-only) means "clear this field"; non-empty rules below

    if field == "date":
        normalized = normalize_date_to_ddmmyyyy(value)
        if not normalized:
            raise HTTPException(
                status_code=400, detail="Enter a real date in DD/MM/YYYY format (year 2000-2100)."
            )
        return normalized

    if field in _AMOUNT_FIELDS:
        cleaned = value.replace(",", "")
        if not AMOUNT_RE.match(cleaned):
            raise HTTPException(
                status_code=400, detail="Enter a plain number (digits only, max 2 decimal places)."
            )
        return cleaned

    if field in _GSTIN_FIELDS:
        cleaned = value.upper().replace(" ", "")
        if GSTIN_RE.match(cleaned) is None:
            raise HTTPException(
                status_code=400, detail="Enter a 15-character GSTIN in the standard format."
            )
        return cleaned

    if field in _PHONE_FIELDS:
        digits = re.sub(r"[^\d]", "", value)
        if PHONE_RE.match(digits) is None:
            raise HTTPException(status_code=400, detail="Enter a 10-digit phone number.")
        return digits

    if not SAFE_TEXT_RE.match(value):
        raise HTTPException(
            status_code=400,
            detail="Enter plain text without control characters or HTML tags (max 300 characters).",
        )
    return value


async def apply_correction(db: Any, doc: dict, field: str, value: str) -> bool:
    """Write the value ONLY if the document is still exactly as it was read (same
    processingRunId, finished). False = it changed (e.g. Reprocess started): nothing was
    written, so the caller must not audit. The corrections row is added only after the
    document write matched."""
    now = datetime.now(UTC)
    # None matches both a missing and a null processingRunId.
    result = await db.documents.update_one(
        {
            "_id": doc["_id"],
            "processingRunId": doc.get("processingRunId"),
            "uploadStatus": {"$in": ["processed", "failed"]},
        },
        {"$set": correction_set_fields(field, value, now)},
    )
    if result.matched_count == 0:
        return False
    await db.corrections.insert_one(
        {
            "documentId": doc["_id"],
            "fieldLabel": field,
            "fieldKey": field,
            "oldValue": doc.get(field),
            "newValue": value,
            "correctedAt": now,
            "createdAt": now,
            "updatedAt": now,
        }
    )
    if field in ("operatorName", "receiptNumber", "date"):
        # Shared by user + admin routes. Duplicates are scoped to the OWNER, not the editor.
        fresh = await db.documents.find_one({"_id": doc["_id"]})
        await refresh_duplicate_flag(db, doc["userId"], doc["_id"], fresh)
    return True
