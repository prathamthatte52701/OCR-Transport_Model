"""dateNeedsReview: a real but implausible date is flagged (never changed)."""

from datetime import date, datetime

import pytest

from app.features.documents.correction import correction_set_fields
from app.features.ocr import extraction as ex
from app.features.ocr.extraction import build_extraction_result, empty_extraction_result

TODAY = date(2026, 6, 15)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("15/06/2026", False),
        ("16/06/2026", False),  # today + 1
        ("17/06/2026", True),  # today + 2
        ("15/06/2021", False),  # exactly 5 years back
        ("14/06/2021", True),  # 5 years back - 1 day
        ("16/06/2021", False),
        ("01/01/2027", True),  # future year
        ("32/13/2026", False),  # unreal -> not flagged
        (None, False),
    ],
)
def test_flag_in_build_result(value: str | None, expected: bool) -> None:
    for doc_type, key in (("Tax Invoice", "taxInvoiceNo"), ("Delivery Challan", "number")):
        r = build_extraction_result(doc_type, {key: "X", "date": value}, today=TODAY)
        assert r["dateNeedsReview"] is expected
        if expected:
            assert r["date"] == value  # value never changed
    assert empty_extraction_result("Tax Invoice")["dateNeedsReview"] is False
    assert empty_extraction_result("Delivery Challan")["dateNeedsReview"] is False


def test_flag_in_flag_fields_and_correction() -> None:
    assert "dateNeedsReview" in ex.EXTRACTION_FLAG_FIELDS
    assert (
        correction_set_fields("date", "01/01/2099", datetime(2026, 1, 1))["dateNeedsReview"]
        is False
    )
    assert "dateNeedsReview" not in correction_set_fields("number", "1", datetime(2026, 1, 1))
