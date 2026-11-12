"""What a manual correction of one extracted field writes - ONE helper used by the user route
(PATCH /documents/{id}/correct) and the admin route, so the two cannot drift apart."""

from datetime import datetime

AUTO_CORRECTED_FIELDS = (
    "date",
    "packageCount",
    "freight",
    "deliveryCharge",
    "demurrage",
    "sgst",
    "cgst",
    "igst",
    "totalAmount",
)
NEEDS_REVIEW_FIELDS = (
    "date",
    "receiptNumber",
    "operatorGstin",
    "consignorGstin",
    "consigneeGstin",
    "consignorPhone",
    "consigneePhone",
    # Amount fields gained their own NeedsReview flag this loop (extraction.py's
    # confusion-map/Baba guards) - a manual correction must clear it too, or a typed-in
    # value stays stuck flagged forever.
    *AUTO_CORRECTED_FIELDS[1:],  # packageCount, freight, deliveryCharge, demurrage, sgst, cgst, igst, totalAmount
)


def correction_set_fields(field: str, value: str, now: datetime) -> dict:
    set_fields: dict = {
        field: value,
        "edited": True,
        "updatedAt": now,
    }
    if field in AUTO_CORRECTED_FIELDS:
        # Manual entry supersedes the auto-correction pass - no longer
        # something the OCR correction layer touched.
        set_fields[f"{field}AutoCorrected"] = False
    if field in NEEDS_REVIEW_FIELDS:
        # The person typed this value - the "looks incomplete" flag no longer applies.
        set_fields[f"{field}NeedsReview"] = False
    return set_fields
