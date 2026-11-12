"""Computes the per-document warning list shown on the review page (spec section 7). Pure
and cheap - recomputed on every read from the document's current (possibly corrected)
field values, never stored, so an edit always updates the warnings immediately with no
separate "recompute" step. Each warning is {"field": <key or None>, "message": <short text>}.

Item 8 (duplicate operator+receiptNumber+date) is NOT computed here - it needs a database
query and is computed/stored separately (see `documents/duplicate.py`), then merged in by
the caller as an extra warning when `doc.get("isDuplicate")` is True.
"""

import re

_AMOUNT_CLEAN_RE = re.compile(r"[,\s]")


def _to_number(value: str) -> float | None:
    if not value:
        return None
    try:
        return float(_AMOUNT_CLEAN_RE.sub("", value))
    except ValueError:
        return None


# ---- amount-in-words parsing (Indian English, "Rupees <words> Only") ----
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}
_SCALE = {"hundred": 100, "thousand": 1000, "lakh": 100_000, "lac": 100_000, "crore": 10_000_000}
_NOISE_WORDS = {"rupees", "rupee", "rs", "inr", "only", "and", "paisa", "paise", "sum", "of"}


def words_to_number(text: str) -> int | None:
    """Best-effort parse of an Indian-English amount-in-words string to an integer. Returns
    None if the text doesn't parse cleanly (never guesses)."""
    if not text:
        return None
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    tokens = [t for t in tokens if t not in _NOISE_WORDS]
    if not tokens:
        return None

    total = 0
    current = 0
    for tok in tokens:
        if tok in _ONES:
            current += _ONES[tok]
        elif tok in _TENS:
            current += _TENS[tok]
        elif tok == "hundred":
            current = (current or 1) * 100
        elif tok in ("thousand", "lakh", "lac", "crore"):
            current = (current or 1) * _SCALE[tok]
            total += current
            current = 0
        else:
            return None  # an unrecognised word: never guess
    return total + current


def _amounts_match(a: float, b: float) -> bool:
    return abs(a - b) < 0.5  # rounding/paisa tolerance


def compute_warnings(doc: dict) -> list[dict]:
    warnings: list[dict] = []

    if not doc.get("receiptNumber"):
        warnings.append({"field": "receiptNumber", "message": "Receipt number missing"})
    elif doc.get("receiptNumberNeedsReview"):
        warnings.append({"field": "receiptNumber", "message": "Receipt number looks incomplete"})

    if not doc.get("date"):
        warnings.append({"field": "date", "message": "Date missing"})
    elif doc.get("dateNeedsReview"):
        warnings.append({"field": "date", "message": "Date looks implausible"})

    if not doc.get("totalAmount"):
        warnings.append({"field": "totalAmount", "message": "Total amount missing"})

    for field, label in (
        ("operatorGstin", "Operator GSTIN"),
        ("consignorGstin", "Consignor GSTIN"),
        ("consigneeGstin", "Consignee GSTIN"),
    ):
        if doc.get(field) and doc.get(f"{field}NeedsReview"):
            warnings.append({"field": field, "message": f"{label} format looks wrong"})

    for field, label in (
        ("consignorPhone", "Consignor phone"),
        ("consigneePhone", "Consignee phone"),
    ):
        if doc.get(field) and doc.get(f"{field}NeedsReview"):
            warnings.append({"field": field, "message": f"{label} looks incomplete"})

    charge_fields = ("freight", "deliveryCharge", "demurrage", "sgst", "cgst", "igst")
    charges = [_to_number(doc.get(f, "")) for f in charge_fields]
    total = _to_number(doc.get("totalAmount", ""))
    parts = [p for p in charges if p is not None]
    if parts and total is not None and not _amounts_match(total, sum(parts)):
        warnings.append(
            {
                "field": "totalAmount",
                "message": "Total does not match freight + delivery + demurrage + taxes",
            }
        )

    words_value = words_to_number(doc.get("amountInWords", ""))
    if words_value is not None and total is not None and not _amounts_match(total, words_value):
        warnings.append({"field": "totalAmount", "message": "Total does not match amount in words"})

    return warnings
