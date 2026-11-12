"""correction_set_fields: a manual correction must reset the field's own NeedsReview flag -
including the amount fields (packageCount/freight/deliveryCharge/demurrage/sgst/cgst/igst/
totalAmount), which gained their own flag this loop (extraction.py's confusion-map/Baba guards)
but were missing from NEEDS_REVIEW_FIELDS, leaving a manually-typed amount stuck flagged."""

from datetime import UTC, datetime

import pytest

from app.features.documents.correction import AUTO_CORRECTED_FIELDS, correction_set_fields

NOW = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize("field", AUTO_CORRECTED_FIELDS)
def test_amount_fields_clear_their_needs_review_flag(field: str) -> None:
    result = correction_set_fields(field, "500", NOW)
    assert result[f"{field}NeedsReview"] is False


def test_date_still_clears_its_flag() -> None:
    assert correction_set_fields("date", "01/01/2026", NOW)["dateNeedsReview"] is False


def test_unrelated_field_has_no_needs_review_key() -> None:
    assert "remarkNeedsReview" not in correction_set_fields("remark", "note", NOW)
