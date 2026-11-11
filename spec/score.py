"""Accuracy scorer for Transport OCR (spec section 15).

strict: exact match after trimming whitespace and lowercasing.
lenient: ignores punctuation/spacing differences, common OCR letter/digit
confusions (on numeric-ish fields only - never on free text, where that
would wrongly equate unrelated words), and date-format differences (any
parseable rendering of the same calendar date counts as a match).

Field lists mirror spec section 5 exactly, split core vs optional so every
report can show both. No AI, no I/O side effects beyond the CLI's own
file reads - the scoring functions are pure.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

CORE_FIELDS = (
    "operator_name",
    "operator_gstin",
    "receipt_number",
    "date",
    "to_place",
    "consignee_name",
    "consignor_name",
    "package_count",
    "payment_mode",
    "total_amount",
    "prepared_by",
)
OPTIONAL_FIELDS = (
    "time",
    "from_place",
    "delivery_address",
    "consignor_gstin",
    "consignor_phone",
    "consignee_gstin",
    "consignee_phone",
    "package_description",
    "freight",
    "delivery_charge",
    "demurrage",
    "sgst",
    "cgst",
    "igst",
    "amount_in_words",
    "remark",
)
ALL_FIELDS = CORE_FIELDS + OPTIONAL_FIELDS

_DATE_FIELDS = {"date"}
_NUMERIC_FIELDS = {
    "receipt_number",
    "operator_gstin",
    "consignor_gstin",
    "consignee_gstin",
    "consignor_phone",
    "consignee_phone",
    "package_count",
    "freight",
    "delivery_charge",
    "demurrage",
    "sgst",
    "cgst",
    "igst",
    "total_amount",
}

# Only applied to numeric-ish fields: a common OCR misread maps to one canonical
# character, so "O" and "0" (etc) compare equal. Never applied to free text (names,
# addresses, remarks), where this would wrongly equate unrelated words.
_CONFUSION_CANON = {
    "o": "0", "0": "0",
    "i": "1", "l": "1", "1": "1",
    "s": "5", "5": "5",
    "z": "2", "2": "2",
    "b": "8", "8": "8",
    "g": "6", "6": "6",
    "d": "0",
}

_DATE_RE = re.compile(r"^(\d{1,2})[./\- ]+(\d{1,2})[./\- ]+(\d{2,4})$")
_PUNCT_RE = re.compile(r"[^\w]", re.UNICODE)


def _strict_norm(value: str) -> str:
    return (value or "").strip().lower()


def _lenient_text_norm(value: str) -> str:
    """Strips punctuation/spacing and lowercases - used for free text and as the
    base pass for numeric fields before the confusion-canon step."""
    return _PUNCT_RE.sub("", (value or "")).lower()


def _lenient_numeric_norm(value: str) -> str:
    base = _lenient_text_norm(value)
    return "".join(_CONFUSION_CANON.get(c, c) for c in base)


def _date_key(value: str) -> str | None:
    """Canonical (year, month, day) string for any DD/MM/YYYY-ish rendering, or
    None if it doesn't parse as a plausible date - never guesses."""
    if not value:
        return None
    m = _DATE_RE.match(value.strip())
    if not m:
        return None
    d, mo, y = m.groups()
    if len(y) == 2:
        y = f"20{y}"
    try:
        d_i, mo_i, y_i = int(d), int(mo), int(y)
    except ValueError:
        return None
    if not (1 <= d_i <= 31 and 1 <= mo_i <= 12 and 1900 <= y_i <= 2100):
        return None
    return f"{y_i:04d}-{mo_i:02d}-{d_i:02d}"


def score_value(field: str, truth: str, pred: str) -> tuple[bool, bool]:
    """Returns (strict_match, lenient_match) for one field of one document."""
    truth, pred = truth or "", pred or ""
    strict = _strict_norm(truth) == _strict_norm(pred)
    if strict:
        return True, True

    if field in _DATE_FIELDS:
        tk, pk = _date_key(truth), _date_key(pred)
        lenient = tk is not None and tk == pk
    elif field in _NUMERIC_FIELDS:
        lenient = _lenient_numeric_norm(truth) == _lenient_numeric_norm(pred)
    else:
        lenient = _lenient_text_norm(truth) == _lenient_text_norm(pred)
    return False, lenient


def score_document(truth_fields: dict[str, Any], pred_fields: dict[str, Any]) -> dict[str, dict]:
    """Per-field {strict, lenient, truth_blank} for every field in ALL_FIELDS.
    truth_blank fields are skipped in aggregate accuracy (spec: optional fields
    are only scored when the truth actually has a value; a field the truth says
    is blank contributes no signal either way)."""
    out: dict[str, dict] = {}
    for field in ALL_FIELDS:
        truth = str(truth_fields.get(field, "") or "")
        pred = str(pred_fields.get(field, "") or "")
        strict, lenient = score_value(field, truth, pred)
        out[field] = {"strict": strict, "lenient": lenient, "truth_blank": truth == ""}
    return out


def aggregate(per_doc: list[dict[str, dict]]) -> dict:
    """Overall + per-field + core/optional accuracy. Only counts fields where the
    truth is non-blank (a correctly-blank prediction is not interesting signal)."""

    def _field_stats(fields: tuple[str, ...]) -> dict:
        total = strict_ok = lenient_ok = 0
        for doc in per_doc:
            for f in fields:
                cell = doc.get(f)
                if cell is None or cell["truth_blank"]:
                    continue
                total += 1
                strict_ok += cell["strict"]
                lenient_ok += cell["lenient"]
        return {
            "total": total,
            "strict": strict_ok,
            "lenient": lenient_ok,
            "strict_pct": round(100 * strict_ok / total, 1) if total else None,
            "lenient_pct": round(100 * lenient_ok / total, 1) if total else None,
        }

    per_field = {f: _field_stats((f,)) for f in ALL_FIELDS}
    return {
        "overall": _field_stats(ALL_FIELDS),
        "core": _field_stats(CORE_FIELDS),
        "optional": _field_stats(OPTIONAL_FIELDS),
        "per_field": per_field,
    }


def worst_fields(agg: dict, n: int = 5) -> list[tuple[str, dict]]:
    scored = [(f, s) for f, s in agg["per_field"].items() if s["total"] > 0]
    scored.sort(key=lambda kv: (kv[1]["strict_pct"], kv[1]["lenient_pct"]))
    return scored[:n]


def _load_ground_truth(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    by_file: dict[str, dict] = {}
    for receipt in data["receipts"]:
        for fname in receipt["files"]:
            by_file[fname] = receipt["fields"]
    return by_file


def _load_results(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", default="spec/ground_truth.json")
    parser.add_argument("--results", required=True, help="CSV with a 'file' column + field columns")
    args = parser.parse_args(argv)

    truth_by_file = _load_ground_truth(Path(args.ground_truth))
    rows = _load_results(Path(args.results))

    per_doc = []
    mismatches: list[tuple[str, str, str, str]] = []
    for row in rows:
        fname = row.get("file", "")
        truth = truth_by_file.get(fname)
        if truth is None:
            print(f"WARNING: no ground truth for {fname!r}, skipping", file=sys.stderr)
            continue
        doc_score = score_document(truth, row)
        per_doc.append(doc_score)
        for field, cell in doc_score.items():
            if not cell["truth_blank"] and not cell["lenient"]:
                mismatches.append((fname, field, truth.get(field, ""), row.get(field, "")))

    agg = aggregate(per_doc)
    print(json.dumps(agg, indent=2))
    print(f"\n{len(mismatches)} lenient mismatches:")
    for fname, field, t, p in mismatches:
        print(f"  {fname} | {field} | truth={t!r} | ocr={p!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
