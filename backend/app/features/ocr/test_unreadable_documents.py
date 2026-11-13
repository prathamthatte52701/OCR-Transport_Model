"""Task 3: a read that fills fewer than 2 of the 11 core fields is a failed read
(OCR_UNREADABLE), never a "processed" document. No real Paddle/Groq."""

from typing import Any

import pytest

from app.features.documents.test_reprocess_reset import (  # noqa: F401 - fixtures + helpers
    Env,
    _insert,
    env,
    reprocess,
    slot,
)
from app.features.ocr import extraction as ex
from app.features.ocr import pipeline
from app.features.ocr.providers import errors

MSG = "We could not read this photo. Try a clearer photo or retry."

PAWAN = {
    "operatorName": "PAWAN TRAVELS", "receiptNumber": "28625", "date": "05/03/2026",
    "toPlace": "PUNE", "consigneeName": "VE COMMERCIAL VEHICLES",
    "consignorName": "KLINGELBERG INDIA", "packageCount": "1", "paymentMode": "Paid",
    "totalAmount": "100", "preparedBy": "PAWAN",
}
BABA = {
    "operatorName": "Baba Travels", "operatorGstin": "23AHQPS8492M1ZA", "receiptNumber": "P97394",
    "date": "16/01/2025", "toPlace": "Ahmedabad", "consigneeName": "Ve Commercial",
    "consignorName": "Self", "packageCount": "3", "paymentMode": "Paid", "totalAmount": "300.00",
}


async def _process(db: Any, make_user: Any, ai_result: dict[str, Any], env: Env) -> dict[str, Any]:
    env.ai = lambda _t: ai_result
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    from app.features.documents.test_reprocess_reset import PNG

    await pipeline.process_document(doc_id, PNG, "image/png")
    d: dict[str, Any] = await db.documents.find_one({"_id": doc_id})
    return d


def test_code_and_message_exist():
    assert errors.OCR_UNREADABLE == "OCR_UNREADABLE"
    assert errors.OCR_UNREADABLE in errors.CODES
    assert errors.user_message(errors.OCR_UNREADABLE) == MSG


@pytest.mark.parametrize("core_filled", [0, 1])
async def test_fewer_than_two_core_fields_is_failed(env: Env, db: Any, make_user: Any, core_filled: int) -> None:
    res = ex.build_extraction_result(dict(list(PAWAN.items())[:core_filled]))
    d = await _process(db, make_user, res, env)
    assert d["uploadStatus"] == "failed"
    assert d["processingErrorCode"] == "OCR_UNREADABLE"
    assert d["processingError"] == MSG
    assert d["ocrTextHidden"] == "NEW OCR TEXT"  # kept so retry / admin can see the text
    assert d.get("processedAt") is None


async def test_exactly_two_core_fields_stays_processed(env: Env, db: Any, make_user: Any) -> None:
    res = ex.build_extraction_result(dict(list(PAWAN.items())[:2]))
    d = await _process(db, make_user, res, env)
    assert d["uploadStatus"] == "processed"
    assert d["processingErrorCode"] is None


async def test_blank_strings_and_flags_do_not_count(env: Env, db: Any, make_user: Any) -> None:
    res = {**dict.fromkeys(ex.EXTRACTION_VALUE_FIELDS, ""), "receiptNumber": "123", "operatorName": "  ",
           "dateNeedsReview": True, "totalAmountNeedsReview": True}
    d = await _process(db, make_user, res, env)
    assert d["uploadStatus"] == "failed" and d["processingErrorCode"] == "OCR_UNREADABLE"


async def test_optional_fields_do_not_make_up_for_missing_core(env: Env, db: Any, make_user: Any) -> None:
    res = ex.build_extraction_result({"time": "10:04 AM", "fromPlace": "INDORE", "freight": "200", "remark": "x"})
    d = await _process(db, make_user, res, env)
    assert d["uploadStatus"] == "failed"


@pytest.mark.parametrize("parsed", [PAWAN, BABA], ids=["real_pawan", "real_baba"])
async def test_real_receipts_stay_processed(env: Env, db: Any, make_user: Any, parsed: dict) -> None:
    d = await _process(db, make_user, ex.build_extraction_result(dict(parsed)), env)
    assert d["uploadStatus"] == "processed"
    assert d["receiptNumber"] == parsed["receiptNumber"]


async def test_unreadable_failure_writes_no_extracted_values(env: Env, db: Any, make_user: Any) -> None:
    d = await _process(db, make_user, ex.build_extraction_result({"receiptNumber": "123"}), env)
    assert d["uploadStatus"] == "failed"
    assert not d.get("receiptNumber")


async def test_reprocess_from_unreadable_state_works(env: Env, client: Any, db: Any, make_user: Any) -> None:
    env.ai = lambda _t: ex.build_extraction_result({"receiptNumber": "123"})
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    from app.features.documents.test_reprocess_reset import PNG

    await pipeline.process_document(doc_id, PNG, "image/png")
    assert (await db.documents.find_one({"_id": doc_id}))["processingErrorCode"] == "OCR_UNREADABLE"
    env.ai = lambda _t: ex.build_extraction_result(dict(PAWAN))  # clearer photo / retry succeeds
    d = await reprocess(client, db, user, doc_id)
    assert d["uploadStatus"] == "processed"
    assert d["processingErrorCode"] is None and d["processingError"] is None
    assert d["receiptNumber"] == "28625"


async def test_unreadable_document_is_counted_failed_with_message(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    """What bulk upload shows: each document is polled; a failed one carries the message."""
    env.ai = lambda _t: ex.build_extraction_result({})
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    from app.features.documents.test_reprocess_reset import PNG

    await pipeline.process_document(doc_id, PNG, "image/png")
    res = await client.get(f"/api/documents/{doc_id}", headers=user.headers)
    assert res.status_code == 200
    body = res.json()["document"]
    assert body["uploadStatus"] == "failed" and body["processingError"] == MSG
    summary = await client.get("/api/documents/summary", headers=user.headers)
    assert summary.status_code == 200
    assert summary.json()["failed"] == 1
