"""Task 3: amounts rebuilt from letters are flagged; fully-fabricated ones are dropped."""
import pytest

from app.features.ocr.extraction import build_extraction_result, correct_amount_format

CASES = [
    # input, expected value, expected totalAmountNeedsReview
    ("OD", "", True),
    ("O", "", True),
    ("5OO", "500", True),
    ("l00", "100", True),
    ("Rs. 500", "500", False),
    ("500/-", "500", False),
    ("1,250.50", "1250.50", False),
    ("500", "500", False),
    ("", "", False),
    ("N/A", "N/A", False),  # unfixable text is kept as printed, as before
]


@pytest.mark.parametrize("raw,expected,review", CASES)
def test_amount_cases(raw, expected, review):
    out = build_extraction_result({"totalAmount": raw})
    print(f"{raw!r:10} -> {out['totalAmount']!r:9} review={out['totalAmountNeedsReview']}")
    assert (out["totalAmount"], out["totalAmountNeedsReview"]) == (expected, review)


def test_correct_amount_format_still_two_tuple():
    assert correct_amount_format("5OO") == ("500", True)


def test_every_amount_field_has_its_own_flag():
    out = build_extraction_result({"freight": "l00", "sgst": "50"})
    assert out["freightNeedsReview"] is True and out["sgstNeedsReview"] is False


@pytest.mark.parametrize("raw,expected,review", [
    ("OD5", "005", True),  # one real digit survives -> kept, flagged
    ("1O.5O", "10.50", True),
    (None, "", False),
    ("Rs.", "", False),  # nothing left after cleanup
    ("SOS", "", True),  # all-letter lookalike -> dropped, flagged
])
def test_amount_break(raw, expected, review):
    out = build_extraction_result({"freight": raw})
    assert (out["freight"], out["freightNeedsReview"]) == (expected, review)
