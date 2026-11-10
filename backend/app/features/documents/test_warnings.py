"""Unit tests for compute_warnings and words_to_number - pure, no DB."""

from app.features.documents.warnings import compute_warnings, words_to_number


def _doc(**overrides: object) -> dict:
    base: dict = {
        "receiptNumber": "P98506",
        "date": "25/02/2025",
        "totalAmount": "200",
        "operatorGstin": "",
        "consignorGstin": "",
        "consigneeGstin": "",
        "consignorPhone": "",
        "consigneePhone": "",
        "freight": "",
        "deliveryCharge": "",
        "demurrage": "",
        "amountInWords": "",
    }
    base.update(overrides)
    return base


def test_clean_document_has_no_warnings() -> None:
    assert compute_warnings(_doc()) == []


def test_missing_receipt_number_date_total() -> None:
    doc = _doc(receiptNumber="", date="", totalAmount="")
    fields = {w["field"] for w in compute_warnings(doc)}
    assert fields == {"receiptNumber", "date", "totalAmount"}


def test_needs_review_flags_produce_warnings() -> None:
    doc = _doc(receiptNumberNeedsReview=True, dateNeedsReview=True)
    msgs = [w["message"] for w in compute_warnings(doc)]
    assert any("incomplete" in m for m in msgs)
    assert any("implausible" in m for m in msgs)


def test_gstin_needs_review_only_when_present() -> None:
    # blank GSTIN never warns even if a stray needsReview flag is set
    doc = _doc(operatorGstin="", operatorGstinNeedsReview=True)
    assert compute_warnings(doc) == []
    doc2 = _doc(operatorGstin="BADGSTIN", operatorGstinNeedsReview=True)
    assert any(w["field"] == "operatorGstin" for w in compute_warnings(doc2))


def test_phone_needs_review_only_when_present() -> None:
    doc = _doc(consignorPhone="", consignorPhoneNeedsReview=True)
    assert compute_warnings(doc) == []
    doc2 = _doc(consignorPhone="12345", consignorPhoneNeedsReview=True)
    assert any(w["field"] == "consignorPhone" for w in compute_warnings(doc2))


def test_total_vs_freight_delivery_demurrage_mismatch() -> None:
    doc = _doc(totalAmount="500", freight="200", deliveryCharge="100", demurrage="100")
    assert any("freight" in w["message"] for w in compute_warnings(doc))
    doc_ok = _doc(totalAmount="400", freight="200", deliveryCharge="100", demurrage="100")
    assert not any("freight" in w["message"] for w in compute_warnings(doc_ok))


def test_total_vs_amount_in_words_mismatch() -> None:
    doc = _doc(totalAmount="200", amountInWords="Rupees Five Hundred Only")
    assert any("amount in words" in w["message"] for w in compute_warnings(doc))
    doc_ok = _doc(totalAmount="200", amountInWords="Rupees Two Hundred Only")
    assert not any("amount in words" in w["message"] for w in compute_warnings(doc_ok))


def test_words_to_number_basic_cases() -> None:
    assert words_to_number("Rupees Two Hundred Only") == 200
    assert words_to_number("Rupees Five Hundred Only") == 500
    assert words_to_number("One Thousand Two Hundred Fifty") == 1250
    assert words_to_number("Twenty Five") == 25
    assert words_to_number("") is None
    assert words_to_number("gibberish nonsense words") is None
