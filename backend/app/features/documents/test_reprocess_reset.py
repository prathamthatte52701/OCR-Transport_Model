"""Reprocess wipes everything a previous read derived (values, flags, hidden text, processedAt,
and a successful read writes every flag explicitly. No real Paddle/Groq."""

import asyncio
import io
import time
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
from bson import ObjectId
from PIL import Image

from app.features.documents import router as docs_router
from app.features.ocr import extraction as ex
from app.features.ocr import pipeline
from app.features.ocr.providers.errors import AIExtractionError

FLAGS = ex.EXTRACTION_FLAG_FIELDS
VALUES = ex.EXTRACTION_VALUE_FIELDS
# keys process_document legitimately adds that are not extraction-derived
ALLOWED_EXTRA = {
    "processingError",
    "processingErrorCode",
    "uploadStatus",
    "updatedAt",
    "reprocessedAt",
    "isDuplicate",
}


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (200, 200), "white").save(buf, format="PNG")
    return buf.getvalue()


PNG = _png()


class Env:
    """Controls the fake OCR engine and fake AI extraction."""

    def __init__(self) -> None:
        self.ocr: Callable[[], Any] = lambda: "NEW OCR TEXT"
        self.ai: Callable[[str], Any] = lambda _t: {}


@pytest.fixture(autouse=True)
def slot() -> Iterator[None]:
    pipeline._reset_slot_for_tests()
    yield
    pipeline._reset_slot_for_tests()


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    e = Env()
    monkeypatch.setattr(pipeline, "run_ocr", lambda _p, **_k: e.ocr())
    monkeypatch.setattr(pipeline, "classify_page_orientation", lambda _b: (0, 1.0))

    async def ai(_text: str, **_k: Any) -> dict[str, Any]:
        out = e.ai(_text)
        if isinstance(out, BaseException):
            raise out
        return dict(out)

    async def download(_file_id: Any) -> bytes:
        return PNG

    monkeypatch.setattr(pipeline, "extract_header", ai)
    monkeypatch.setattr(docs_router, "download_buffer", download)
    return e


def _const(res: dict[str, Any]) -> Callable[[str], Any]:
    return lambda _t: res


def result(**over: Any) -> dict[str, Any]:
    base = ex.build_extraction_result(
        {"receiptNumber": "28625", "operatorName": "ACME", "date": "01/01/2026"}
    )
    return {**base, **over}


async def _insert(db: Any, user: Any, **extra: Any) -> Any:
    doc = {
        "userId": user.id,
        "uploadStatus": "processed",
        "isDeleted": False,
        "originalName": "a.png",
        "gridFsFileId": ObjectId(),
        "mimeType": "image/png",
        "createdAt": datetime.now(UTC),
        **extra,
    }
    return (await db.documents.insert_one(doc)).inserted_id


def stale(**over: Any) -> dict[str, Any]:
    """A fully processed, fully flagged old document."""
    d: dict[str, Any] = {
        **dict.fromkeys(VALUES, "OLD"),
        "receiptNumber": "OLD-RN",
        "operatorName": "OLD-OP",
        "totalAmount": "999",
        "date": "09/09/2020",
        **dict.fromkeys(FLAGS, True),
        "ocrTextHidden": "old text",
        "processedAt": datetime(2020, 1, 1, tzinfo=UTC),
        "edited": True,
    }
    d.update(over)
    return d


async def reprocess(client: Any, db: Any, user: Any, doc_id: Any, expect: int = 200) -> dict:
    res = await client.post(f"/api/documents/{doc_id}/reprocess", headers=user.headers)
    assert res.status_code == expect, res.text
    if expect >= 400:
        return {}
    end = time.monotonic() + 10
    while True:
        d = await db.documents.find_one({"_id": doc_id})
        if d["uploadStatus"] in ("processed", "failed") and d.get("reprocessedAt"):
            return dict(d)
        assert time.monotonic() < end, f"reprocess did not finish: {d}"
        await asyncio.sleep(0.02)


def assert_clean_failed(d: dict[str, Any]) -> None:
    assert d["uploadStatus"] == "failed"
    assert all(d[k] == "" for k in VALUES), d
    assert all(d[f] is False for f in FLAGS), d
    assert d["processedAt"] is None
    assert d["edited"] is False


# 1
async def test_engine_error_leaves_clean_state(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    def boom() -> Any:
        raise RuntimeError("engine boom")

    env.ocr = boom
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    d = await reprocess(client, db, user, doc_id)
    assert_clean_failed(d)
    assert d["ocrTextHidden"] is None


# 2
async def test_ai_failure_leaves_clean_state(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    env.ai = lambda _t: AIExtractionError("RATE_LIMIT")
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    d = await reprocess(client, db, user, doc_id)
    assert_clean_failed(d)
    assert d["processingErrorCode"]
    assert d["ocrTextHidden"] == "NEW OCR TEXT" != "old text"


# 3
async def test_success_missing_flags_end_false(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    partial = {"receiptNumber": "TR/1", "date": "01/01/2026"}
    env.ai = lambda _t: partial
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    d = await reprocess(client, db, user, doc_id)
    assert d["uploadStatus"] == "processed"
    assert all(d[f] is False for f in FLAGS), d
    assert d["receiptNumber"] == "TR/1" and d["totalAmount"] == ""
    assert d["processedAt"].replace(tzinfo=None) > datetime(2021, 1, 1)
    assert d["ocrTextHidden"] == "NEW OCR TEXT"

    env.ai = lambda _t: {**partial, "receiptNumberNeedsReview": True}
    d = await reprocess(client, db, user, doc_id)
    assert d["receiptNumberNeedsReview"] is True
    assert d["operatorGstinNeedsReview"] is False and d["totalAmountAutoCorrected"] is False


# 4
async def test_clean_read_clears_stale_flags(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    env.ai = lambda _t: result()
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    d = await reprocess(client, db, user, doc_id)
    assert d["uploadStatus"] == "processed"
    assert all(d[f] is False for f in FLAGS), d


# 5
async def test_first_time_processing_writes_all_flags(env: Env, db: Any, make_user: Any) -> None:
    user = await make_user()
    res = result()
    env.ai = _const(res)
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    await pipeline.process_document(doc_id, PNG, "image/png")
    d = await db.documents.find_one({"_id": doc_id})
    assert d["uploadStatus"] == "processed"
    assert all(isinstance(d[f], bool) for f in FLAGS), d
    for k in VALUES:
        assert d[k] == res.get(k)


# 6
async def test_edited_document_replaced_by_new_read(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    env.ai = lambda _t: result()
    user = await make_user()
    doc_id = await _insert(
        db, user, **stale(receiptNumber="HAND-EDIT", dateAutoCorrected=True)
    )
    d = await reprocess(client, db, user, doc_id)
    assert d["edited"] is False
    assert d["receiptNumber"] == result()["receiptNumber"]
    for f in FLAGS:
        assert d[f] == bool(result().get(f, False)), f


# 7
async def test_recovery_of_legacy_uploaded_document(env: Env, db: Any, make_user: Any) -> None:
    env.ai = lambda _t: result()
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    assert await docs_router.recover_interrupted_uploads() == 1
    d = await db.documents.find_one({"_id": doc_id})
    assert d["uploadStatus"] == "processed"
    assert all(isinstance(d[f], bool) for f in FLAGS), d


# 8
async def test_api_hides_internal_keys(env: Env, client: Any, db: Any, make_user: Any) -> None:
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    res = await client.get(f"/api/documents/{doc_id}", headers=user.headers)
    assert res.status_code == 200, res.text
    body = res.json()
    doc = body.get("document", body)
    assert "ocrTextHidden" not in doc
    for k in (*VALUES, *FLAGS):
        assert k in doc, k


# 9
async def test_drift_guard(env: Env, db: Any, make_user: Any) -> None:
    derived = set(ex.EXTRACTION_DERIVED_FIELDS)
    ops = ex.extraction_reset_ops()
    assert set(ops) == {"$set"} and set(ops["$set"]) == derived
    res = result()
    assert set(res) <= derived, set(res) - derived
    env.ai = _const(res)
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="uploaded")
    before = set(await db.documents.find_one({"_id": doc_id}))
    await pipeline.process_document(doc_id, PNG, "image/png")
    after = set(await db.documents.find_one({"_id": doc_id}))
    assert (after - before) <= derived | ALLOWED_EXTRA, (after - before) - derived


# 10
async def test_other_users_document_404(env: Env, client: Any, db: Any, make_user: Any) -> None:
    owner, other = await make_user(), await make_user()
    doc_id = await _insert(db, owner, **stale())
    await reprocess(client, db, other, doc_id, expect=404)
    assert (await db.documents.find_one({"_id": doc_id}))["receiptNumber"] == "OLD-RN"


async def test_purged_file_400_and_untouched(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    user = await make_user()
    doc_id = await _insert(db, user, filePurged=True, **stale())
    await reprocess(client, db, user, doc_id, expect=400)
    d = await db.documents.find_one({"_id": doc_id})
    assert d["receiptNumber"] == "OLD-RN" and d["receiptNumberNeedsReview"] is True


# 11
async def test_reprocess_after_failed_reprocess(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    env.ai = lambda _t: AIExtractionError("RATE_LIMIT")
    user = await make_user()
    doc_id = await _insert(db, user, **stale())
    assert_clean_failed(await reprocess(client, db, user, doc_id))
    env.ai = lambda _t: result()
    d = await reprocess(client, db, user, doc_id)
    assert d["uploadStatus"] == "processed"
    assert d["processingError"] is None and d["processingErrorCode"] is None
    assert d["receiptNumber"] == result()["receiptNumber"]


# 12
async def test_legacy_document_without_flags(
    env: Env, client: Any, db: Any, make_user: Any
) -> None:
    def boom() -> Any:
        raise RuntimeError("x")

    env.ocr = boom
    user = await make_user()
    doc_id = await _insert(db, user, uploadStatus="failed", receiptNumber="X")
    d = await reprocess(client, db, user, doc_id)
    assert all(d[f] is False for f in FLAGS)
    assert all(d[k] == "" for k in VALUES)


# 13
def test_reset_ops_shape() -> None:
    ops = ex.extraction_reset_ops()
    assert set(ops) == {"$set"}
    s = ops["$set"]
    assert all(s[k] == "" for k in VALUES)
    assert s["ocrTextHidden"] is None and s["processedAt"] is None
    assert all(s[f] is False for f in FLAGS)
    assert isinstance(ex.EXTRACTION_DERIVED_FIELDS, tuple)
    assert set(ex.EXTRACTION_DERIVED_FIELDS) == {*VALUES, *FLAGS, "ocrTextHidden", "processedAt"}


def test_success_fields_empty_and_partial() -> None:
    empty = ex.extraction_success_fields({})
    assert all(empty[k] == "" for k in VALUES)
    assert all(empty[f] is False for f in FLAGS)
    assert set(empty) == {*VALUES, *FLAGS}

    part = ex.extraction_success_fields(
        {"receiptNumber": "N1", "receiptNumberNeedsReview": True, "dateAutoCorrected": 1, "junk": "x"}
    )
    assert part["receiptNumber"] == "N1" and part["date"] == ""
    assert part["receiptNumberNeedsReview"] is True and part["dateAutoCorrected"] is True
    assert part["operatorGstinNeedsReview"] is False
    assert "junk" not in part
