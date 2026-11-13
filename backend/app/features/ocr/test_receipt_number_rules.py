"""Task 4: receipt number shape rules per operator + the receiptNumberAutoCorrected flag."""
from datetime import UTC, datetime

import pytest

from app.features.documents.correction import correction_set_fields
from app.features.ocr import extraction as ex

BABA = "Baba Travels"
PAWAN = "PAWAN TRAVELS"


def run(operator: str, number: str) -> tuple[str, bool, bool]:
    out = ex.build_extraction_result({"operatorName": operator, "receiptNumber": number})
    return out["receiptNumber"], out["receiptNumberNeedsReview"], out["receiptNumberAutoCorrected"]


# (operator, raw, stored value, needsReview, autoCorrected)
CASES = [
    (BABA, "P98SO6", "P98506", False, True),    # letter confusion after the P prefix repaired
    (BABA, "98506", "98506", True, False),      # 5 digits, no P: probably a dropped P
    (BABA, "186,798", "186,798", False, False),  # printed form kept as is, valid
    (BABA, "P8851", "P8851", False, False),
    (PAWAN, "38420", "38420", False, False),
    (PAWAN, "P38420", "P38420", True, False),   # Pawan has no letter prefix
    (PAWAN, "GrNo38420", "38420", False, True),  # label strip is a repair
]


@pytest.mark.parametrize("operator,raw,value,review,auto", CASES)
def test_named_cases(operator, raw, value, review, auto):
    assert run(operator, raw) == (value, review, auto)


@pytest.mark.parametrize(
    "operator,raw,value,review,auto",
    [
        (BABA, "P98506", "P98506", False, False),   # clean P + 5 digits
        (BABA, "P9850", "P9850", False, False),     # P + 4 digits valid
        (BABA, "186798", "186798", False, False),   # 6 digits valid
        (BABA, "1234567", "1234567", True, False),  # 7 digits
        (BABA, "P123", "P123", True, False),        # too short
        (BABA, "PP98506", "PP98506", True, False),  # double prefix: never guessed
        (BABA, "P98SO6 ", "P98506", False, True),   # surrounding space
        (BABA, "GrNo P98506", "P98506", False, True),
        (BABA, "02/2025", "02/2025", True, False),  # garbage is flagged, not repaired
        (PAWAN, "98506", "98506", False, False),    # plain 5 digits is Pawan's shape
        (PAWAN, "186798", "186798", True, False),   # 6 digits is not Pawan's shape
        (PAWAN, "Gr No : 38420", "38420", False, True),
        (PAWAN, "P98SO6", "P98506", True, True),    # repaired AND still not Pawan-shaped
        (BABA, "", "", False, False),
        (PAWAN, "", "", False, False),
    ],
)
def test_brutal_and_break_cases(operator, raw, value, review, auto):
    assert run(operator, raw) == (value, review, auto)


def test_unknown_operator_keeps_the_loose_shape_rule():
    assert run("", "38420") == ("38420", False, False)
    assert run("", "P98506") == ("P98506", False, False)
    assert run("", "TR/2526/000123")[1] is True


def test_non_p_letter_digit_mix_is_flagged_never_fixed():
    assert run(BABA, "98SO6") == ("98SO6", True, False)
    assert run(PAWAN, "3S420") == ("3S420", True, False)


def test_flag_is_in_the_schema_and_reset_ops():
    assert "receiptNumberAutoCorrected" in ex.EXTRACTION_FLAG_FIELDS
    assert ex.extraction_reset_ops()["$set"]["receiptNumberAutoCorrected"] is False
    assert ex.empty_extraction_result()["receiptNumberAutoCorrected"] is False
    assert ex.extraction_success_fields({"receiptNumberAutoCorrected": True})["receiptNumberAutoCorrected"] is True


def test_manual_edit_clears_both_flags():
    sets = correction_set_fields("receiptNumber", "P98506", datetime.now(UTC))
    assert sets["receiptNumberAutoCorrected"] is False
    assert sets["receiptNumberNeedsReview"] is False
    other = correction_set_fields("toPlace", "Pune", datetime.now(UTC))
    assert "receiptNumberAutoCorrected" not in other


def test_other_auto_corrected_flags_still_cleared_by_their_own_edit():
    for field in ("date", "totalAmount", "freight", "operatorGstin"):
        assert correction_set_fields(field, "x", datetime.now(UTC))[f"{field}AutoCorrected"] is False
    assert correction_set_fields("totalAmount", "1", datetime.now(UTC))["totalAmountNeedsReview"] is False
