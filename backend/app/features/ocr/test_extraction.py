"""Smoke test for the Transport field schema's deterministic post-processing pass.
Run directly: python -m app.features.ocr.test_extraction"""

from app.features.ocr.extraction import (
    build_extraction_result,
    correct_amount_format,
    correct_date_format,
    empty_extraction_result,
    normalize_gstin,
    normalize_phone,
)


def test_amount_confusion_corrected() -> None:
    corrected, was_corrected = correct_amount_format("2OO")
    assert was_corrected is True
    assert corrected == "200"


def test_amount_strips_commas_and_currency() -> None:
    corrected, was_corrected = correct_amount_format("1,200.50")
    assert corrected == "1200.50"


def test_date_confusion_corrected() -> None:
    corrected, was_corrected = correct_date_format("O1/07/2O26")
    assert was_corrected is True
    assert corrected == "01/07/2026"


def test_gstin_uppercased_not_rejected_on_bad_shape() -> None:
    value, needs_review = normalize_gstin("27aaeck1993k1z3")
    assert value == "27AAECK1993K1Z3" and needs_review is False
    bad_value, needs_review = normalize_gstin("not-a-gstin")
    assert bad_value == "NOT-A-GSTIN" and needs_review is True


def test_phone_0000000000_kept_exactly() -> None:
    value, needs_review = normalize_phone("0000000000")
    assert value == "0000000000" and needs_review is False


def test_phone_wrong_length_flagged_not_changed() -> None:
    value, needs_review = normalize_phone("12345")
    assert value == "12345" and needs_review is True


def test_build_extraction_result_end_to_end() -> None:
    result = build_extraction_result(
        {
            "operatorName": "Baba Travels",
            "operatorGstin": "23ahqps8492m1za",
            "receiptNumber": "P98506",
            "date": "O1/07/2O26",
            "totalAmount": "2OO",
        }
    )
    assert result["operatorName"] == "Baba Travels"
    assert result["operatorGstin"] == "23AHQPS8492M1ZA"
    assert result["date"] == "01/07/2026" and result["dateAutoCorrected"] is True
    assert result["totalAmount"] == "200" and result["totalAmountAutoCorrected"] is True


def test_package_count_split_from_glued_description() -> None:
    # Real case: the AI left "2Parcel" whole in packageDescription instead of
    # splitting out the count - the deterministic fallback catches it.
    result = build_extraction_result({"packageDescription": "2Parcel"})
    assert result["packageCount"] == "2" and result["packageDescription"] == "Parcel"


def test_package_count_split_with_space() -> None:
    result = build_extraction_result({"packageDescription": "10 Parcel"})
    assert result["packageCount"] == "10" and result["packageDescription"] == "Parcel"


def test_package_count_not_touched_when_already_present() -> None:
    result = build_extraction_result({"packageCount": "3", "packageDescription": "2Parcel"})
    # packageCount already set by the AI - the fallback never overrides a real value
    assert result["packageCount"] == "3" and result["packageDescription"] == "2Parcel"


def test_results_carry_every_value_and_flag_field() -> None:
    from app.features.ocr.extraction import EXTRACTION_FLAG_FIELDS, EXTRACTION_VALUE_FIELDS

    result = build_extraction_result({"receiptNumber": "P1", "date": "01/07/2026"})
    empty = empty_extraction_result()
    for field in (*EXTRACTION_VALUE_FIELDS, *EXTRACTION_FLAG_FIELDS):
        assert field in result
        assert field in empty


def test_receipt_number_shape_flagged_not_changed() -> None:
    flagged = build_extraction_result({"receiptNumber": "!!"})
    assert flagged["receiptNumber"] == "!!" and flagged["receiptNumberNeedsReview"] is True
    ok = build_extraction_result({"receiptNumber": "P98506"})
    assert ok["receiptNumberNeedsReview"] is False
    assert build_extraction_result({})["receiptNumberNeedsReview"] is False


def test_empty_result_is_all_blank_and_false() -> None:
    result = empty_extraction_result()
    for key, value in result.items():
        if key.endswith("NeedsReview") or key.endswith("AutoCorrected"):
            assert value is False
        else:
            assert value == ""


def demo() -> None:
    test_amount_confusion_corrected()
    test_amount_strips_commas_and_currency()
    test_date_confusion_corrected()
    test_gstin_uppercased_not_rejected_on_bad_shape()
    test_phone_0000000000_kept_exactly()
    test_phone_wrong_length_flagged_not_changed()
    test_build_extraction_result_end_to_end()
    test_package_count_split_from_glued_description()
    test_package_count_split_with_space()
    test_package_count_not_touched_when_already_present()
    test_results_carry_every_value_and_flag_field()
    test_receipt_number_shape_flagged_not_changed()
    test_empty_result_is_all_blank_and_false()
    print("All extraction/correction self-checks passed.")


if __name__ == "__main__":
    demo()
