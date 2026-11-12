"""I5: an empty value clears any field on both the user and admin correction routes."""

from datetime import UTC, datetime
from typing import Any

import pytest

from app.features.ocr.extraction import EXTRACTION_VALUE_FIELDS


async def _doc(db: Any, owner: Any, **extra: Any) -> Any:
    now = datetime.now(UTC)
    res = await db.documents.insert_one(
        {
            "userId": owner.id, "originalFilename": "a.png", "uploadStatus": "processed",
            "processingRunId": "r1", "isDeleted": False, "edited": False,
            "createdAt": now, "updatedAt": now, **extra,
        }
    )
    return res.inserted_id


def _url(route: str, doc_id: Any) -> str:
    return f"/api/documents/{doc_id}/correct" if route == "user" else f"/api/admin/documents/{doc_id}"


async def _patch(client: Any, route: str, acct: Any, doc_id: Any, field: str, value: str) -> Any:
    return await client.patch(
        _url(route, doc_id), headers=acct.headers, json={"field": field, "value": value}
    )


@pytest.mark.parametrize("route", ["user", "admin"])
async def test_clear_receipt_number(client: Any, db: Any, make_user: Any, route: str) -> None:
    owner = await make_user()
    acct = owner if route == "user" else await make_user(role="admin")
    d = await _doc(db, owner, receiptNumber="R9", receiptNumberNeedsReview=True)
    r = await _patch(client, route, acct, d, "receiptNumber", "")
    assert r.status_code == 200, r.text
    row = await db.documents.find_one({"_id": d})
    assert row["receiptNumber"] == "" and row["receiptNumberNeedsReview"] is False
    h = await db.corrections.find_one({"documentId": d, "fieldKey": "receiptNumber"})
    assert h["oldValue"] == "R9" and h["newValue"] == ""


@pytest.mark.parametrize("route", ["user", "admin"])
@pytest.mark.parametrize("field", sorted(EXTRACTION_VALUE_FIELDS))
async def test_every_field_clears(
    client: Any, db: Any, make_user: Any, route: str, field: str
) -> None:
    owner = await make_user()
    acct = owner if route == "user" else await make_user(role="admin")
    d = await _doc(db, owner, **{field: "x"})
    r = await _patch(client, route, acct, d, field, "")
    assert r.status_code == 200, (field, r.text)
    assert (await db.documents.find_one({"_id": d}))[field] == ""


async def test_clear_blank_noop_reset_and_rerun_duplicate(
    client: Any, db: Any, make_user: Any
) -> None:
    u = await make_user()
    keys = {"operatorName": "Pawan Travels", "receiptNumber": "D1", "date": "01/02/2024"}
    a = await _doc(db, u, **keys)
    b = await _doc(db, u, **keys)
    assert (await _patch(client, "user", u, b, "date", "01/02/2024")).status_code == 200
    assert (await db.documents.find_one({"_id": b}))["isDuplicate"] is True
    # clearing a key field refreshes the duplicate flag
    assert (await _patch(client, "user", u, b, "date", "")).status_code == 200
    assert (await db.documents.find_one({"_id": b}))["isDuplicate"] is False
    # already-blank optional field: no-op success
    assert (await _patch(client, "user", u, a, "consignorGstin", "")).status_code == 200
    # clear then set again
    assert (await _patch(client, "user", u, a, "receiptNumber", "")).status_code == 200
    assert (await _patch(client, "user", u, a, "receiptNumber", "Z5")).status_code == 200
    assert (await db.documents.find_one({"_id": a}))["receiptNumber"] == "Z5"


async def test_break_attempts(client: Any, db: Any, make_user: Any) -> None:
    owner, other = await make_user(), await make_user()
    d = await _doc(db, owner, consigneeName="Bob")
    # whitespace-only counts as empty -> clears (value is stripped before validation)
    assert (await _patch(client, "user", owner, d, "consigneeName", "   ")).status_code == 200
    assert (await db.documents.find_one({"_id": d}))["consigneeName"] == ""
    # non-empty validation is unchanged
    assert (await _patch(client, "user", owner, d, "consigneeName", "a" * 301)).status_code == 400
    assert (await _patch(client, "user", owner, d, "date", "garbage")).status_code == 400
    # unknown field still rejected; clearing does not bypass ownership
    assert (await _patch(client, "user", owner, d, "nope", "")).status_code == 400
    d2 = await _doc(db, owner, consigneeName="Keep")
    assert (await _patch(client, "user", other, d2, "consigneeName", "")).status_code == 404
    assert (await db.documents.find_one({"_id": d2}))["consigneeName"] == "Keep"
    # a normal user cannot use the admin route
    assert (await _patch(client, "admin", owner, d2, "consigneeName", "")).status_code in (401, 403)
    # mid-processing doc still blocked
    d3 = await _doc(db, owner, uploadStatus="processing", consigneeName="Q")
    assert (await _patch(client, "user", owner, d3, "consigneeName", "")).status_code == 409
