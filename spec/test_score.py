"""Unit tests for score.py on tiny synthetic cases - run before trusting it on real data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from score import (  # noqa: E402
    aggregate,
    score_document,
    score_value,
    worst_fields,
)


def test_strict_exact_match() -> None:
    assert score_value("operator_name", "PAWAN TRAVELS", "PAWAN TRAVELS") == (True, True)


def test_strict_case_and_space_insensitive() -> None:
    assert score_value("operator_name", "Pawan Travels", "  pawan travels  ") == (True, True)


def test_strict_fails_on_real_difference() -> None:
    strict, lenient = score_value("operator_name", "Pawan Travels", "Baba Travels")
    assert strict is False and lenient is False


def test_lenient_text_ignores_punctuation() -> None:
    strict, lenient = score_value("package_description", "PARCEL - PARCEL", "PARCEL-PARCEL")
    assert strict is False and lenient is True


def test_lenient_numeric_confusion_swap() -> None:
    # O/0, I/1 etc are only swapped for numeric-ish fields, never free text
    strict, lenient = score_value("receipt_number", "P98O1O", "P9801O".replace("O", "0"))
    assert lenient is True


def test_lenient_numeric_does_not_equate_unrelated_text() -> None:
    # "to" and "t0" would collide under a blind confusion swap - but this is a text
    # field, so the swap must never apply here
    strict, lenient = score_value("consignee_name", "Self", "Shelf")
    assert strict is False and lenient is False


def test_date_lenient_matches_different_separators() -> None:
    strict, lenient = score_value("date", "25/02/2025", "25.02.2025")
    assert strict is False and lenient is True


def test_date_lenient_matches_two_digit_year() -> None:
    strict, lenient = score_value("date", "25/02/2025", "25/02/25")
    assert lenient is True


def test_date_lenient_rejects_a_different_date() -> None:
    strict, lenient = score_value("date", "25/02/2025", "26/02/2025")
    assert strict is False and lenient is False


def test_date_lenient_rejects_unparseable_garbage() -> None:
    strict, lenient = score_value("date", "25/02/2025", "not a date")
    assert strict is False and lenient is False


def test_both_blank_counts_as_strict_match() -> None:
    assert score_value("remark", "", "") == (True, True)


def test_score_document_covers_every_field() -> None:
    truth = {"operator_name": "Pawan Travels", "date": "01/01/2025"}
    pred = {"operator_name": "Pawan Travels", "date": "01/01/2025"}
    result = score_document(truth, pred)
    assert result["operator_name"]["strict"] is True
    assert result["remark"]["truth_blank"] is True  # not in truth dict -> blank
    assert len(result) == 27  # all 11 core + 16 optional fields


def test_aggregate_skips_blank_truth_fields() -> None:
    per_doc = [
        score_document({"operator_name": "A", "remark": ""}, {"operator_name": "A", "remark": "X"})
    ]
    agg = aggregate(per_doc)
    # remark truth is blank -> not counted even though prediction differs
    assert agg["per_field"]["remark"]["total"] == 0
    assert agg["per_field"]["operator_name"]["total"] == 1
    assert agg["per_field"]["operator_name"]["strict"] == 1


def test_aggregate_core_vs_optional_split() -> None:
    per_doc = [
        score_document(
            {"operator_name": "A", "time": "10:00"},
            {"operator_name": "A", "time": "wrong"},
        )
    ]
    agg = aggregate(per_doc)
    assert agg["core"]["total"] == 1 and agg["core"]["strict"] == 1
    assert agg["optional"]["total"] == 1 and agg["optional"]["strict"] == 0


def test_worst_fields_ranks_lowest_accuracy_first() -> None:
    per_doc = [
        score_document(
            {"operator_name": "A", "remark": "B"},
            {"operator_name": "A", "remark": "wrong"},
        )
    ]
    agg = aggregate(per_doc)
    worst = worst_fields(agg, n=2)
    assert worst[0][0] == "remark"  # 0% accuracy, ranked worst
    assert worst[0][1]["strict_pct"] == 0.0


def test_empty_prediction_never_crashes() -> None:
    strict, lenient = score_value("total_amount", "200", "")
    assert strict is False and lenient is False


def test_none_like_missing_keys_treated_as_blank() -> None:
    result = score_document({"operator_name": "A"}, {})
    assert result["operator_name"]["strict"] is False
    assert result["operator_name"]["truth_blank"] is False
