"""Task 4: deterministic post-AI checks (no AI call)."""
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


def test_baba_freight_equal_total_cleared():
    out = build({"operatorName": "Baba Travels", "freight": "250", "totalAmount": "250"})
    assert out["freight"] == "" and out["totalAmount"] == "250"
    assert out["totalAmountNeedsReview"] is False


def test_baba_freight_equal_total_after_cleanup_cleared():
    out = build({"operatorName": "Baba Travels", "freight": "Rs. 250/-", "totalAmount": "250"})
    assert out["freight"] == ""


def test_baba_different_freight_kept():
    out = build({"operatorName": "Baba Travels", "freight": "200", "totalAmount": "250"})
    assert out["freight"] == "200"


def test_pawan_freight_equal_total_kept():
    out = build({"operatorName": "Pawan Travels", "freight": "250", "totalAmount": "250"})
    assert out["freight"] == "250"
