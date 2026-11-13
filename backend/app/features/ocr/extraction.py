"""Transport receipt field schema and the deterministic post-processing pass that runs on
every AI extraction result. No AI involved in this file.

One flat field list (camelCase keys) covers both operator layouts (Pawan Travels, Baba
Travels). Every field is a plain string; empty string when absent (never None - that
distinction does not exist for a receipt, unlike ACKN's "not read yet" vs "confirmed
absent"). Core fields are the ones present on most receipts; optional fields are everything
else. Accuracy reporting always splits core vs optional (spec section 5/15)."""

import difflib
import math
import re
from datetime import date as date_type
from datetime import datetime
from typing import Any

from loguru import logger

from app.core.date_window import date_implausible
from app.core.timezones import now_ist

DATE_RE = re.compile(r"^(\d{1,2})[./\-\s](\d{1,2})[./\-\s](\d{2}|\d{4})$")
DATE_CHARS_RE = re.compile(r"^[\d./\- ]+$")
_AMOUNT_NOISE_RE = re.compile(r"(?:rs\.?|inr|₹)\s*", re.IGNORECASE)
_AMOUNT_TRAILING_WORDS_RE = re.compile(r"\b(only)\b\s*", re.IGNORECASE)
# A two-digit year is only expanded when the result lands in a plausible receipt window.
_TWO_DIGIT_YEAR_MIN, _TWO_DIGIT_YEAR_MAX = 2000, 2099
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
    """Accepts day/month with 1-2 digits and a 2 or 4 digit year, any of . / - or space as
    separator. A 2-digit year expands to 20YY only inside the plausible receipt window. Zero-pads
    day/month on output. Anything that still doesn't resolve to a real calendar date -> None."""
    if not raw or not isinstance(raw, str):
        return None
    match = DATE_RE.match(raw.strip())
    if not match:
        return None
    dd, mm, yyyy = match.groups()
    d, m = int(dd), int(mm)
    if len(yyyy) == 4:
        y = int(yyyy)
        if not 2000 <= y <= 2100:
            return None
    else:
        y = 2000 + int(yyyy)
        if not _TWO_DIGIT_YEAR_MIN <= y <= _TWO_DIGIT_YEAR_MAX:
            return None
    try:
        datetime(y, m, d)
    except ValueError:
        return None
    return f"{d:02d}/{m:02d}/{y:04d}"


def _corrected_date(raw_date: str | None) -> tuple[str, bool]:
    """Returns (value, auto_corrected). Value is a clean DD/MM/YYYY when parseable; otherwise the
    trimmed raw text is kept (never blanked - I4: losing the raw value loses information a human
    could still read)."""
    date = normalize_date_to_ddmmyyyy(raw_date)
    if date is not None:
        return date, False
    corrected_raw, was_corrected = correct_date_format(raw_date)
    if was_corrected:
        corrected_date = normalize_date_to_ddmmyyyy(corrected_raw)
        if corrected_date is not None:
            return corrected_date, True
    raw = raw_date.strip() if isinstance(raw_date, str) else ""
    return raw[:_MAX_FIELD_LENGTH], False


# ---- Group 1: date/time deterministic repairs (flag when unsure, rewrite only when certain) ----
_MONTH_FULL = ("january", "february", "march", "april", "may", "june", "july", "august",
               "september", "october", "november", "december")
_DATE_TIME_SPLIT_RE = re.compile(
    r"^(.*\d.*?)[\s,]+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp]\.?\s?[Mm]\.?)?)$")
_DATE_MONTHNAME_RE = re.compile(r"^(\d{1,2})[\s.\-/,]*([A-Za-z0-9]{3,9})[\s.\-/,]*(\d{4}|\d{2})$")
# a "/" read as 7 or 1: DD?MM/YYYY or DD/MM?YYYY
_DATE_SLASH_MISREAD_RES = (
    re.compile(r"^(\d{2})[71](\d{2})/(\d{4})$"),
    re.compile(r"^(\d{2})/(\d{2})[71](\d{4})$"),
)
_TIME_12H_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp])\.?\s?[Mm]\.?$")
_TIME_24H_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")


def _resolve_month(token: str) -> tuple[int | None, bool]:
    """(month 1-12 or None, exact). A noisy name resolves only when exactly ONE month is a
    single-letter miss (3 letters) or a >=0.8 close match (longer); ambiguity -> None."""
    t = token.lower().replace("0", "o")
    for i, full in enumerate(_MONTH_FULL, 1):
        if t == full or t == full[:3] or (i == 9 and t == "sept"):
            return i, True
    if len(t) == 3:
        hits = [i for i, full in enumerate(_MONTH_FULL, 1) if sum(a != b for a, b in zip(t, full[:3])) == 1]
    else:
        hits = [i for i, full in enumerate(_MONTH_FULL, 1) if difflib.SequenceMatcher(None, t, full).ratio() >= 0.8]
    return (hits[0], False) if len(hits) == 1 else (None, False)


def _real_date(d: int, m: int, y: int) -> str | None:
    if not 2000 <= y <= 2100:
        return None
    try:
        datetime(y, m, d)
    except ValueError:
        return None
    return f"{d:02d}/{m:02d}/{y:04d}"


def _repair_date(raw: str) -> tuple[str, bool, bool]:
    """(date text, auto_corrected, month_name_style). Only returns a rewritten value when it is a
    real calendar date; otherwise the input comes back unchanged."""
    if normalize_date_to_ddmmyyyy(raw):
        return raw, False, False
    m = _DATE_MONTHNAME_RE.match(raw)
    if m and re.search(r"[A-Za-z]", m.group(2)):
        month, exact = _resolve_month(m.group(2))
        y = int(m.group(3))
        y = y + 2000 if len(m.group(3)) == 2 else y
        fixed = _real_date(int(m.group(1)), month, y) if month else None
        return (fixed, not exact, True) if fixed else (raw, False, True)
    for rx in _DATE_SLASH_MISREAD_RES:
        m = rx.match(raw)
        if m:
            fixed = _real_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if fixed:
                return fixed, True, False
    return raw, False, False


def normalize_time(raw: str) -> tuple[str, bool]:
    """(value, needs_review). 'H:MM AM/PM' for 12-hour, 'HH:MM[:SS]' for 24-hour; out-of-range
    or unrecognised text is returned unchanged and flagged."""
    t = raw.strip()
    m = _TIME_12H_RE.match(t)
    if m:
        h, mi, sec = int(m.group(1)), m.group(2), m.group(3)
        if 1 <= h <= 12 and int(mi) < 60 and (sec is None or int(sec) < 60):
            return f"{h}:{mi}{':' + sec if sec else ''} {m.group(4).upper()}M", False
        return raw, True
    m = _TIME_24H_RE.match(t)
    if m:
        h, mi, sec = int(m.group(1)), m.group(2), m.group(3)
        if h <= 23 and int(mi) < 60 and (sec is None or int(sec) < 60):
            return f"{h:02d}:{mi}{':' + sec if sec else ''}", False
    return raw, bool(t)


def correct_amount_format(value: str | None) -> tuple[str, bool]:
    corrected, auto, _ = _clean_amount(value)
    return corrected, auto


def _clean_amount(value: str | None) -> tuple[str, bool, bool]:
    """Returns (value, auto_corrected, needs_review); needs_review is True only when letters
    were turned into digits. Digit-only field (money amounts, package count): strip commas/currency noise, then run
    the confusion map. Returns (possibly-corrected value, was_auto_corrected). On failure to
    reach a clean plain-number shape, returns the trimmed ORIGINAL text unchanged."""
    if not value or not isinstance(value, str):
        return "", False, False
    # Only strip thousands separators/currency marks/trailing "/-"/"Only" noise, never digits
    # or the decimal point.
    cleaned = value.strip()
    cleaned = _AMOUNT_NOISE_RE.sub("", cleaned)
    cleaned = _AMOUNT_TRAILING_WORDS_RE.sub("", cleaned)
    cleaned = re.sub(r"[,]", "", cleaned)
    cleaned = cleaned.strip().rstrip("/-").strip()
    if not cleaned:
        return "", False, False
    if AMOUNT_RE.match(cleaned):
        return cleaned, cleaned != value.strip(), False
    chars = list(cleaned)
    _apply_confusion_map(chars, allowed={"."})
    corrected = "".join(chars)
    if AMOUNT_RE.match(corrected):
        # Letters were turned into digits. If no digit was ever printed, the value is pure
        # invention ("OD" -> "00"): drop it, still flagged so a human looks.
        return (corrected if any(c.isdigit() for c in cleaned) else ""), True, True
    return value.strip()[:_MAX_FIELD_LENGTH], False, False


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
    elif isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            text = None
        elif value == int(value):
            text = str(int(value))
        else:
            text = repr(value)
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
    "timeNeedsReview",
    "operatorGstinNeedsReview",
    "consignorGstinNeedsReview",
    "consigneeGstinNeedsReview",
    "consignorPhoneNeedsReview",
    "consigneePhoneNeedsReview",
    *(f"{f}AutoCorrected" for f in _AMOUNT_FIELDS),
    *(f"{f}NeedsReview" for f in _AMOUNT_FIELDS),
)
EXTRACTION_DERIVED_FIELDS = (
    *EXTRACTION_VALUE_FIELDS,
    *EXTRACTION_FLAG_FIELDS,
    "ocrTextHidden",
    "processedAt",
)


# "Fright"/"Freight"/"Frt" and OCR-noisy spellings ("Fraght", "Frieght", "FRIGHT:").
FREIGHT_LABEL_RE = re.compile(r"\bfr[a-z]{0,2}g[hn]?t|\bfrt\b", re.IGNORECASE)


def build_extraction_result(
    parsed: Any, today: date_type | None = None, ocr_text: str | None = None
) -> dict:
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

    # Group 1: a time baked into the date text moves to `time` (only if empty), then month-name
    # and misread-slash repairs; a Baba receipt never prints a month name -> suspicious.
    split = _DATE_TIME_SPLIT_RE.match(out["date"])
    if split:
        out["date"] = split.group(1).strip()
        out["time"] = out["time"] or split.group(2).strip()
    out["date"], repaired, month_named = _repair_date(out["date"])
    date, auto = _corrected_date(out["date"])
    out["dateAutoCorrected"] = auto or repaired
    out["date"] = date
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date) and normalize_date_to_ddmmyyyy(date):
        out["dateNeedsReview"] = date_implausible(date, today or now_ist().date())
    else:
        out["dateNeedsReview"] = bool(date)  # non-empty but unparseable -> flag for review
    if month_named and "baba" in out["operatorName"].lower():
        out["dateNeedsReview"] = True
    out["time"], out["timeNeedsReview"] = normalize_time(out["time"]) if out["time"] else ("", False)

    for field in _AMOUNT_FIELDS:
        corrected, auto, review = _clean_amount(out[field])
        out[field] = corrected
        out[f"{field}AutoCorrected"] = auto
        # Letters-to-digits substitution is a guess, not a read: always ask for review.
        # (Plain cleanup like "Rs. 500" or "500/-" is AutoCorrected but not NeedsReview.)
        out[f"{field}NeedsReview"] = review

    # Baba-only rules (Baba has no separate delivery address, and a lone "Amount" gets copied
    # into both totalAmount and freight). Only fires when operatorName clearly says Baba.
    # Rule 5 (freight == totalAmount) only clears freight when the OCR text has no freight label
    # at all; a printed "Fright" label means the value is real. No OCR text -> can't tell, so keep
    # the value and flag it for a human.
    if "baba" in out["operatorName"].lower():
        if out["deliveryAddress"].strip().lower() == out["toPlace"].strip().lower():
            out["deliveryAddress"] = ""
        if out["freight"] and out["freight"] == out["totalAmount"]:
            if ocr_text is None:
                out["freightNeedsReview"] = True
            elif not FREIGHT_LABEL_RE.search(ocr_text):
                out["freight"] = ""
                out["freightAutoCorrected"] = out["freightNeedsReview"] = False

    # A lone freight with no total and no other charge/tax: the total is probably missed.
    if out["freight"] and not any(
        out[f] for f in ("totalAmount", "deliveryCharge", "demurrage", "sgst", "cgst", "igst")
    ):
        out["totalAmountNeedsReview"] = True

    for field in _GSTIN_FIELDS:
        value, needs_review = normalize_gstin(out[field])
        out[field] = value
        out[f"{field}NeedsReview"] = needs_review

    for field in _PHONE_FIELDS:
        value, needs_review = normalize_phone(out[field])
        out[field] = value
        out[f"{field}NeedsReview"] = needs_review

    # Fallback split for "2Parcel"/"4 Parcel"-shaped packageDescription values the AI
    # left unsplit: a leading count glued to the description is unambiguous and safe
    # to split deterministically (never invents a count that wasn't already there).
    if not out["packageCount"]:
        m = re.match(r"^(\d+)\s*(\D.*)$", out["packageDescription"])
        if m:
            out["packageCount"], out["packageDescription"] = m.group(1), m.group(2).strip()

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
