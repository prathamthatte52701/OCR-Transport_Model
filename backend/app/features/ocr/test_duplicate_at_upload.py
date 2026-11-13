"""Task 5: duplicate flags are set when a document is saved as processed - BOTH copies end up
flagged (the earlier copy too), also when two copies finish at the same moment. Fake Mongo."""
import asyncio
from typing import Any

import pytest

from app.features.documents.test_reprocess_reset import (  # noqa: F401 - fixtures + helpers
    PNG,
    Env,
    _insert,
    env,
    slot,
)
from app.features.ocr import extraction as ex
from app.features.ocr import pipeline

KEY = {
    "operatorName": "PAWAN TRAVELS", "receiptNumber": "28625", "date": "05/03/2026",
    "toPlace": "PUNE", "consigneeName": "VE COMMERCIAL VEHICLES",
    "consignorName": "KLINGELBERG INDIA", "packageCount": "1", "paymentMode": "Paid",
    "totalAmount": "100", "preparedBy": "PAWAN",
}


async def _new(db: Any, user: Any) -> Any:
    return await _insert(db, user, uploadStatus="uploaded")


async def _flag(db: Any, doc_id: Any) -> Any:
    d = await db.documents.find_one({"_id": doc_id})
    assert d["uploadStatus"] == "processed", d
    return d["isDuplicate"]


async def _process(doc_id: Any) -> None:
    await pipeline.process_document(doc_id, PNG, "image/png")


@pytest.fixture
def same_key(env: Env) -> Env:
    env.ai = lambda _t: ex.build_extraction_result(dict(KEY))
    return env


async def test_two_copies_one_after_another_both_flagged(same_key, db, make_user):
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    await _process(a)
    assert await _flag(db, a) is False  # alone, nothing to match yet
    await _process(b)
    assert await _flag(db, b) is True
    assert await _flag(db, a) is True  # the EARLIER copy is flagged too


async def test_three_copies_all_flagged(same_key, db, make_user):
    user = await make_user()
    ids = [await _new(db, user) for _ in range(3)]
    for i in ids:
        await _process(i)
    assert [await _flag(db, i) for i in ids] == [True, True, True]


@pytest.mark.parametrize("round_no", range(10))
async def test_two_copies_processed_at_the_same_moment_both_flagged(
    same_key, db, make_user, monkeypatch, round_no
):
    """Both jobs reach the AI step, wait for each other there, then are released together."""
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    arrived = 0
    release = asyncio.Event()

    async def ai(_text: str, **_k: Any) -> dict[str, Any]:
        nonlocal arrived
        arrived += 1
        if arrived == 2:
            release.set()
        await asyncio.wait_for(release.wait(), 10)
        return ex.build_extraction_result(dict(KEY))

    monkeypatch.setattr(pipeline, "extract_header", ai)
    await asyncio.wait_for(asyncio.gather(_process(a), _process(b)), 30)
    assert await _flag(db, a) is True
    assert await _flag(db, b) is True


async def test_check_runs_after_the_document_write_is_committed(same_key, db, make_user, monkeypatch):
    user = await make_user()
    a = await _new(db, user)
    seen: list[str] = []
    real = pipeline.refresh_duplicate_flag

    async def spy(db_: Any, user_id: Any, doc_id: Any, doc: dict) -> bool:
        stored = await db_.documents.find_one({"_id": doc_id})
        seen.append(stored["uploadStatus"])
        assert stored["receiptNumber"] == "28625"  # the values the check compares are stored
        return await real(db_, user_id, doc_id, doc)

    monkeypatch.setattr(pipeline, "refresh_duplicate_flag", spy)
    await _process(a)
    assert seen == ["processed"]


async def test_different_users_never_affect_each_other(same_key, db, make_user):
    u1, u2 = await make_user(), await make_user()
    a, b = await _new(db, u1), await _new(db, u2)
    await _process(a)
    await _process(b)
    assert await _flag(db, a) is False and await _flag(db, b) is False
    a2 = await _new(db, u1)
    await _process(a2)
    assert await _flag(db, a) is True and await _flag(db, a2) is True
    assert await _flag(db, b) is False  # the other user's copy is untouched


async def test_case_and_spacing_do_not_hide_a_duplicate(same_key, db, make_user):
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    same_key.ai = lambda _t: ex.build_extraction_result({**KEY, "operatorName": "pawan  travels"})
    await _process(a)
    same_key.ai = lambda _t: ex.build_extraction_result(dict(KEY))
    await _process(b)
    assert await _flag(db, a) is True and await _flag(db, b) is True


async def test_blank_key_is_never_a_duplicate(same_key, db, make_user):
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    same_key.ai = lambda _t: ex.build_extraction_result({**KEY, "receiptNumber": ""})
    await _process(a)
    await _process(b)
    assert await _flag(db, a) is False and await _flag(db, b) is False


async def test_a_deleted_copy_is_not_a_match(same_key, db, make_user):
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    await _process(a)
    await db.documents.update_one({"_id": a}, {"$set": {"isDeleted": True}})
    await _process(b)
    assert await _flag(db, b) is False


async def test_edited_to_a_different_key_loses_its_flag(same_key, client, db, make_user):
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    await _process(a)
    await _process(b)
    assert await _flag(db, a) is True and await _flag(db, b) is True
    res = await client.patch(
        f"/api/documents/{b}/correct", headers=user.headers,
        json={"field": "receiptNumber", "value": "99999"},
    )
    assert res.status_code == 200, res.text
    assert await _flag(db, a) is False  # partner is no longer a duplicate
    assert await _flag(db, b) is False


async def test_stale_job_does_not_flag_anything(same_key, db, make_user):
    """A job that lost its document to a newer run writes nothing, and does not flag peers."""
    user = await make_user()
    a, b = await _new(db, user), await _new(db, user)
    await _process(a)
    await db.documents.update_one({"_id": b}, {"$set": {"processingRunId": "newer-run"}})
    await pipeline.process_document(b, PNG, "image/png", run_id="old-run")
    assert (await db.documents.find_one({"_id": b}))["uploadStatus"] == "uploaded"
    assert await _flag(db, a) is False
