"""Transport receipt field schema and the deterministic post-processing pass that runs on
every AI extraction result. No AI involved in this file.

One flat field list (camelCase keys) covers both operator layouts (Pawan Travels, Baba
Travels). Every field is a plain string; empty string when absent (never None - that
distinction does not exist for a receipt, unlike ACKN's "not read yet" vs "confirmed
absent"). Core fields are the ones present on most receipts; optional fields are everything
else. Accuracy reporting always splits core vs optional (spec section 5/15)."""

import re
from datetime import date as date_type
from datetime import datetime
from typing import Any

from loguru import logger

from app.core.date_window import date_implausible
from app.core.timezones import now_ist

DATE_RE = re.compile(r"^(\d{2})[./-](\d{2})[./-](\d{4})$")
DATE_CHARS_RE = re.compile(r"^[\d./-]+$")
GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
PHONE_RE = re.compile(r"^\d{10}$")
# A receipt number must have at least one letter-or-digit run of reasonable length; this is a
# shape check only (never changed or rejected), matching spec item 7 ("looks incomplete").
RECEIPT_NUMBER_SHAPE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ,/-]{1,19}$")
# A plain amount: digits only, optional one decimal point with 1-2 places (commas/currency
# symbols are stripped before this check runs).
AMOUNT_RE = re.compile(r"^\d+(\.\d{1,2})?$")

# Classic OCR character-confusion pairs, letter -> the digit it's most often misread as.
# Applied ONLY to fields that are always plain digits (money amounts, package count) - never
# to receiptNumber, which is alphanumeric by design (e.g. "P98506").
_CONFUSION_MAP = {
    "I": "1", "l": "1", "O": "0", "o": "0", "Z": "2", "z": "2",
    "S": "5", "s": "5", "B": "8", "b": "8", "G": "6", "g": "6", "D": "0", "d": "0",
}

_MAX_FIELD_LENGTH = 300  # long enough for delivery_address / amount_in_words / remark


def _apply_confusion_map(chars: list[str], allowed: set[str]) -> bool:
    changed = False
    for i, c in enumerate(chars):
        if c in allowed or c.isdigit():
            continue
        mapped = _CONFUSION_MAP.get(c)
        if mapped is not None:
            chars[i] = mapped
            changed = True
    return changed


def correct_date_format(raw_date: str | None) -> tuple[str | None, bool]:
    """Same character-confusion correction, applied to the date field only."""
    if not raw_date or not isinstance(raw_date, str):
        return raw_date, False
    stripped = raw_date.strip()
    if not stripped:
        return raw_date, False
    chars = list(stripped)
    changed = _apply_confusion_map(chars, allowed=set("./-"))
    if not changed:
        return raw_date, False
    corrected = "".join(chars)
    if DATE_CHARS_RE.match(corrected):
        return corrected, True
    return raw_date, False


def normalize_date_to_ddmmyyyy(raw: str | None) -> str | None:
    """Never guess: only accepts an already-unambiguous DD/MM/YYYY-shaped value (separator
    normalized to /). Anything else -> empty string."""
    if not raw or not isinstance(raw, str):
        return None
    match = DATE_RE.match(raw.strip())
    if not match:
        return None
    dd, mm, yyyy = match.groups()
    d, m, y = int(dd), int(mm), int(yyyy)
    if not 2000 <= y <= 2100:
        return None
    try:
        datetime(y, m, d)
    except ValueError:
        return None
    return f"{dd}/{mm}/{yyyy}"


def _corrected_date(raw_date: str | None) -> tuple[str, bool]:
    date = normalize_date_to_ddmmyyyy(raw_date)
    if date is not None:
        return date, False
    corrected_raw, was_corrected = correct_date_format(raw_date)
    if was_corrected:
        corrected_date = normalize_date_to_ddmmyyyy(corrected_raw)
        if corrected_date is not None:
            return corrected_date, True
    return "", False


def correct_amount_format(value: str | None) -> tuple[str, bool]:
    """Digit-only field (money amounts, package count): strip commas/currency noise, then run
    the confusion map. Returns (possibly-corrected value, was_auto_corrected). On failure to
    reach a clean plain-number shape, returns the trimmed ORIGINAL text unchanged."""
    if not value or not isinstance(value, str):
        return "", False
    # Only strip thousands separators/currency marks, never digits or the decimal point.
    cleaned = re.sub(r"[,₹]|rs\.?|RS\.?", "", value.strip()).strip()
    if not cleaned:
        return "", False
    if AMOUNT_RE.match(cleaned):
        return cleaned, cleaned != value.strip()
    chars = list(cleaned)
    changed = _apply_confusion_map(chars, allowed={"."})
    corrected = "".join(chars)
    if AMOUNT_RE.match(corrected):
        return corrected, True
    return value.strip()[:_MAX_FIELD_LENGTH], False


def normalize_gstin(value: str | None) -> tuple[str, bool]:
    """Uppercase only (GSTIN letters are never case-sensitive in practice); never invents or
    drops a character. Returns (value, needs_review) where needs_review is True when the
    15-char GSTIN shape does not match (flag only, value is kept as printed)."""
    if not value or not isinstance(value, str):
        return "", False
    cleaned = value.strip().upper().replace(" ", "")
    if not cleaned:
        return "", False
    return cleaned, GSTIN_RE.match(cleaned) is None


def normalize_phone(value: str | None) -> tuple[str, bool]:
    """Digits only (spaces/dashes stripped); 0000000000 is kept exactly and accepted. Returns
    (value, needs_review)."""
    if not value or not isinstance(value, str):
        return "", False
    digits = re.sub(r"[^\d]", "", value.strip())
    if not digits:
        return "", False
    return digits, PHONE_RE.match(digits) is None


def _clean_text_field(value: Any, field: str) -> str:
    """Every AI value goes through here: only a string (trimmed) or a whole number the model
    returned as JSON survives; everything else is "not read" (empty string). Never guesses,
    never joins list items, never truncates silently below the max length - logs and drops
    instead. Logs the field and python type only, never the value."""
    text: str | None = None
    if isinstance(value, str):
        text = value.strip()
    elif isinstance(value, bool):
        pass
    elif isinstance(value, int):
        text = str(value)
    elif isinstance(value, float) and value == int(value):
        text = str(int(value))
    if text is not None and 0 < len(text) <= _MAX_FIELD_LENGTH:
        return text
    if value is not None and not (isinstance(value, str) and not text):
        logger.warning("AI value for {} dropped (type {})", field, type(value).__name__)
    return ""


# ---- Single source of truth for the Transport field schema. ----
# Every value field a read can write, in display order. Core fields are present on most
# receipts (spec section 5); everything else is optional. Both tuples are used by Reprocess
# (to wipe them all) and by process_document (to write them all), so they cannot drift apart.
CORE_FIELDS = (
    "operatorName",
    "operatorGstin",
    "receiptNumber",
    "date",
    "toPlace",
    "consigneeName",
    "consignorName",
    "packageCount",
    "paymentMode",
    "totalAmount",
    "preparedBy",
)
OPTIONAL_FIELDS = (
    "time",
    "fromPlace",
    "deliveryAddress",
    "consignorGstin",
    "consignorPhone",
    "consigneeGstin",
    "consigneePhone",
    "packageDescription",
    "freight",
    "deliveryCharge",
    "demurrage",
    "sgst",
    "cgst",
    "igst",
    "amountInWords",
    "remark",
)
EXTRACTION_VALUE_FIELDS = CORE_FIELDS + OPTIONAL_FIELDS

# Amount-shaped fields: digits only, confusion-map corrected.
_AMOUNT_FIELDS = ("packageCount", "freight", "deliveryCharge", "demurrage", "sgst", "cgst", "igst", "totalAmount")
_GSTIN_FIELDS = ("operatorGstin", "consignorGstin", "consigneeGstin")
_PHONE_FIELDS = ("consignorPhone", "consigneePhone")

EXTRACTION_FLAG_FIELDS = (
    "dateAutoCorrected",
    "dateNeedsReview",
    "receiptNumberNeedsReview",
    "operatorGstinNeedsReview",
    "consignorGstinNeedsReview",
    "consigneeGstinNeedsReview",
    "consignorPhoneNeedsReview",
    "consigneePhoneNeedsReview",
    *(f"{f}AutoCorrected" for f in _AMOUNT_FIELDS),
)
EXTRACTION_DERIVED_FIELDS = (
    *EXTRACTION_VALUE_FIELDS,
    *EXTRACTION_FLAG_FIELDS,
    "ocrTextHidden",
    "processedAt",
)


def build_extraction_result(parsed: Any, today: date_type | None = None) -> dict:
    """Applies a deterministic rule-based correction pass (OCR character-confusion fixes on
    numeric fields, date normalisation, GSTIN/phone shape flags) to the raw field dict already
    parsed from the AI response. Correction never invents a digit or letter - it only fixes a
    value that fails validation into one that passes; anything it can't resolve falls through
    unchanged (as printed)."""
    if not isinstance(parsed, dict):
        return empty_extraction_result()

    out: dict[str, Any] = {}
    for field in EXTRACTION_VALUE_FIELDS:
        out[field] = _clean_text_field(parsed.get(field), field)

    date, out["dateAutoCorrected"] = _corrected_date(out["date"])
    out["date"] = date
    out["dateNeedsReview"] = date_implausible(date or None, today or now_ist().date())

    for field in _AMOUNT_FIELDS:
        corrected, auto = correct_amount_format(out[field])
        out[field] = corrected
        out[f"{field}AutoCorrected"] = auto

    for field in _GSTIN_FIELDS:
        value, needs_review = normalize_gstin(out[field])
        out[field] = value
        out[f"{field}NeedsReview"] = needs_review

    for field in _PHONE_FIELDS:
        value, needs_review = normalize_phone(out[field])
        out[field] = value
        out[f"{field}NeedsReview"] = needs_review

    receipt = out["receiptNumber"]
    out["receiptNumberNeedsReview"] = bool(receipt) and RECEIPT_NUMBER_SHAPE_RE.match(receipt) is None

    return out


def empty_extraction_result() -> dict:
    out: dict[str, Any] = {field: "" for field in EXTRACTION_VALUE_FIELDS}
    out.update({field: False for field in EXTRACTION_FLAG_FIELDS})
    return out


def extraction_reset_ops() -> dict:
    """Mongo update operators that wipe everything a previous read left behind: values empty
    string, flags False, the old OCR text and processedAt None."""
    to_set: dict = {field: "" for field in EXTRACTION_VALUE_FIELDS}
    to_set.update({field: False for field in EXTRACTION_FLAG_FIELDS})
    to_set["ocrTextHidden"] = None
    to_set["processedAt"] = None
    return {"$set": to_set}


def extraction_success_fields(result: dict) -> dict:
    """What a successful read writes: every value (empty string when the result lacks one) and
    every flag explicitly True/False - a flag missing from the result is False, never stale."""
    fields: dict = {field: result.get(field, "") for field in EXTRACTION_VALUE_FIELDS}
    fields.update({field: bool(result.get(field, False)) for field in EXTRACTION_FLAG_FIELDS})
    return fields
