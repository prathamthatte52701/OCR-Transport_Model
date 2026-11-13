"""Task 4: deterministic post-AI checks (no AI call)."""
import pytest

from app.features.ocr.extraction import build_extraction_result as build

GOOD_GSTIN = "27AAPFU0939F1ZV"


def test_gstin_valid_no_flag():
    assert build({"consignorGstin": GOOD_GSTIN})["consignorGstinNeedsReview"] is False


def test_gstin_bad_shape_flagged_value_kept():
    out = build({"consignorGstin": "27AAPFU0939F1Z"})
    assert out["consignorGstin"] == "27AAPFU0939F1Z" and out["consignorGstinNeedsReview"] is True


def test_phone_ok_and_zero_special_case():
    assert build({"consignorPhone": "9876543210"})["consignorPhoneNeedsReview"] is False
    assert build({"consignorPhone": "0000000000"})["consignorPhoneNeedsReview"] is False


def test_phone_nine_digits_flagged():
    out = build({"consignorPhone": "987654321"})
    assert out["consignorPhone"] == "987654321" and out["consignorPhoneNeedsReview"] is True


def test_freight_only_blank_total_flagged():
    out = build({"freight": "100"})
    assert out["totalAmount"] == "" and out["totalAmountNeedsReview"] is True


def test_freight_and_total_not_flagged():
    assert build({"freight": "100", "totalAmount": "100"})["totalAmountNeedsReview"] is False


def test_freight_with_other_charge_blank_total_not_flagged():
    assert build({"freight": "100", "deliveryCharge": "10"})["totalAmountNeedsReview"] is False


def test_nothing_at_all_not_flagged():
    assert build({})["totalAmountNeedsReview"] is False


def test_baba_delivery_address_equal_to_toplace_cleared():
    out = build({"operatorName": "Baba Travels", "toPlace": "Nagpur", "deliveryAddress": " nagpur "})
    assert out["deliveryAddress"] == "" and out["toPlace"] == "Nagpur"


def test_baba_different_delivery_address_kept():
    out = build({"operatorName": "BABA TRAVELS", "toPlace": "Nagpur", "deliveryAddress": "Sitabuldi"})
    assert out["deliveryAddress"] == "Sitabuldi"


def test_pawan_delivery_address_equal_to_toplace_kept():
    out = build({"operatorName": "Pawan Travels", "toPlace": "Nagpur", "deliveryAddress": "Nagpur"})
    assert out["deliveryAddress"] == "Nagpur"


def test_blank_operator_never_guessed_as_baba():
    out = build({"toPlace": "Nagpur", "deliveryAddress": "Nagpur", "freight": "5", "totalAmount": "5"})
    assert out["deliveryAddress"] == "Nagpur" and out["freight"] == "5"


BABA_EQ = {"operatorName": "Baba Travels", "freight": "250", "totalAmount": "250"}
NO_LABEL_TEXT = "BABA TRAVELS\nP98506 05/03/2026\nDetail: 1 Parcel\nAmount 250"


def test_baba_freight_equal_total_cleared_when_no_freight_label_in_ocr():
    out = build(BABA_EQ, ocr_text=NO_LABEL_TEXT)
    assert out["freight"] == "" and out["totalAmount"] == "250"
    assert out["totalAmountNeedsReview"] is False and out["freightNeedsReview"] is False


def test_baba_freight_equal_total_after_cleanup_cleared_when_no_label():
    out = build(
        {"operatorName": "Baba Travels", "freight": "Rs. 250/-", "totalAmount": "250"},
        ocr_text=NO_LABEL_TEXT,
    )
    assert out["freight"] == ""


def test_baba_real_printed_fright_label_keeps_equal_freight():
    out = build(
        {"operatorName": "Baba Travels", "freight": "100", "totalAmount": "100"},
        ocr_text="BABA TRAVELS\nFright 100\nAmount 100",
    )
    assert out["freight"] == "100" and out["freightNeedsReview"] is False


@pytest.mark.parametrize(
    "label",
    ["Fraght 250", "Fright : 250", "FRIGHT:250", "Freight   250", "Frieght 250", "Frt 250"],
)
def test_baba_misspelled_freight_label_keeps_freight(label):
    out = build(BABA_EQ, ocr_text=f"BABA TRAVELS\n{label}\nAmount 250")
    assert out["freight"] == "250"


def test_baba_without_ocr_text_keeps_freight_and_flags_review():
    out = build(BABA_EQ)  # old caller / no raw text: never guess
    assert out["freight"] == "250" and out["freightNeedsReview"] is True


def test_baba_empty_ocr_text_string_is_text_without_label_so_clears():
    assert build(BABA_EQ, ocr_text="")["freight"] == ""


@pytest.mark.parametrize("text", [None, NO_LABEL_TEXT, "Fright 250"])
def test_pawan_is_untouched_by_the_baba_freight_rule(text):
    out = build(
        {"operatorName": "Pawan Travels", "freight": "250", "totalAmount": "250"}, ocr_text=text
    )
    assert out["freight"] == "250" and out["freightNeedsReview"] is False


def test_extract_header_passes_raw_ocr_text_through():
    import asyncio

    from app.features.ocr.ai_extraction import extract_header

    class P:
        async def extract(self, _s, _u):
            return '{"operatorName": "Baba Travels", "freight": "250", "totalAmount": "250"}'

    out = asyncio.run(extract_header(NO_LABEL_TEXT, provider=P()))
    assert out["freight"] == ""
    out = asyncio.run(extract_header(NO_LABEL_TEXT + "\nFright 250", provider=P()))
    assert out["freight"] == "250"


def test_baba_different_freight_kept():
    out = build({"operatorName": "Baba Travels", "freight": "200", "totalAmount": "250"})
    assert out["freight"] == "200"


def test_pawan_freight_equal_total_kept():
    out = build({"operatorName": "Pawan Travels", "freight": "250", "totalAmount": "250"})
    assert out["freight"] == "250"


def test_prompt_delivery_address_allows_separate_line_only():
    from app.features.ocr.ai_extraction import _env, _TEMPLATE
    from app.features.ocr.extraction import EXTRACTION_VALUE_FIELDS
    p = _env.get_template(_TEMPLATE).render(field_count=len(EXTRACTION_VALUE_FIELDS))
    assert "must always be null" not in p
    assert "fill it only if the receipt prints a SEPARATE delivery address line" in p
    assert "never copy the \"Delivery At\" value" in p
