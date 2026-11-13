"""Correction refreshes isDuplicate / NeedsReview identically on the user and admin routes."""

from datetime import UTC, datetime
from typing import Any

import pytest

ROUTES = ["user", "admin"]


async def _doc(db: Any, owner: Any, **extra: Any) -> Any:
    now = datetime.now(UTC)
    base = {
        "userId": owner.id,
        "originalFilename": "a.png",
        "uploadStatus": "processed",
        "processingRunId": "run1",
        "operatorName": "Baba Travels",
        "receiptNumber": "P1",
        "date": "25/02/2025",
        "totalAmount": "100",
        "isDeleted": False,
        "isDuplicate": False,
        "edited": False,
        "createdAt": now,
        "updatedAt": now,
    }
    base.update(extra)
    return (await db.documents.insert_one(base)).inserted_id


async def _patch(client: Any, route: str, owner: Any, make_user: Any, doc_id: Any, f: str, v: str):
    if route == "user":
        return await client.patch(
            f"/api/documents/{doc_id}/correct", headers=owner.headers, json={"field": f, "value": v}
        )
    admin = await make_user(role="admin")
    return await client.patch(
        f"/api/admin/documents/{doc_id}", headers=admin.headers, json={"field": f, "value": v}
    )


async def _flags(db: Any, doc_id: Any) -> dict:
    d = await db.documents.find_one({"_id": doc_id})
    return {k: d.get(k) for k in ("isDuplicate", "receiptNumberNeedsReview", "dateNeedsReview")}


@pytest.mark.parametrize("route", ROUTES)
async def test_fix_receipt_number_clears_duplicate(client, db, make_user, route) -> None:
    u = await make_user()
    await _doc(db, u)
    d = await _doc(db, u, isDuplicate=True)
    r = await _patch(client, route, u, make_user, d, "receiptNumber", "P2")
    assert r.status_code == 200
    assert (await _flags(db, d))["isDuplicate"] is False


@pytest.mark.parametrize("route", ROUTES)
async def test_edit_to_match_other_sets_duplicate(client, db, make_user, route) -> None:
    u = await make_user()
    await _doc(db, u)
    d = await _doc(db, u, receiptNumber="P9")
    await _patch(client, route, u, make_user, d, "receiptNumber", "p1")
    assert (await _flags(db, d))["isDuplicate"] is True


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("field", ["receiptNumber", "date", "totalAmount"])
async def test_clearing_core_field_shows_in_needs_review(
    client, db, make_user, route, field
) -> None:
    u = await make_user()
    d = await _doc(db, u, receiptNumberNeedsReview=True, dateNeedsReview=True)
    r = await _patch(client, route, u, make_user, d, field, "")
    assert r.status_code == 200
    got = await client.get("/api/documents?needsReview=true", headers=u.headers)
    assert str(d) in [x["id"] if "id" in x else x.get("_id") for x in got.json()["documents"]]
    f = await _flags(db, d)
    if field != "totalAmount":
        assert f[f"{field}NeedsReview"] is False


@pytest.mark.parametrize("route", ROUTES)
async def test_clear_receipt_number_drops_duplicate(client, db, make_user, route) -> None:
    u = await make_user()
    await _doc(db, u)
    d = await _doc(db, u, isDuplicate=True)
    await _patch(client, route, u, make_user, d, "receiptNumber", "")
    assert (await _flags(db, d))["isDuplicate"] is False


async def test_user_and_admin_end_in_same_state(client, db, make_user) -> None:
    u = await make_user()
    await _doc(db, u)
    out = {}
    for route in ROUTES:
        d = await _doc(db, u, receiptNumber="P9", receiptNumberNeedsReview=True)
        await _patch(client, route, u, make_user, d, "receiptNumber", "P1")
        out[route] = await _flags(db, d)
    assert out["user"] == out["admin"] and out["user"]["isDuplicate"] is True


@pytest.mark.parametrize("route", ROUTES)
async def test_brutal_repeat_edits_and_unrelated_field(client, db, make_user, route) -> None:
    u = await make_user()
    await _doc(db, u)
    d = await _doc(db, u, receiptNumber="P9")
    for v, want in [("P1", True), ("P1", True), ("P5", False), ("P1", True)]:
        await _patch(client, route, u, make_user, d, "receiptNumber", v)
        assert (await _flags(db, d))["isDuplicate"] is want
    # unrelated field must not touch isDuplicate (even if it was stale-set by hand)
    await db.documents.update_one({"_id": d}, {"$set": {"isDuplicate": False}})
    await _patch(client, route, u, make_user, d, "consignorName", "Ram")
    assert (await _flags(db, d))["isDuplicate"] is False


@pytest.mark.parametrize("route", ROUTES)
async def test_break_blank_receipts_never_duplicate(client, db, make_user, route) -> None:
    u = await make_user()
    await _doc(db, u, receiptNumber="")
    d = await _doc(db, u, receiptNumber="X")
    await _patch(client, route, u, make_user, d, "receiptNumber", "")
    assert (await _flags(db, d))["isDuplicate"] is False


# --- Peer refresh: editing/deleting one doc re-checks the OTHER docs sharing its old/new key ---


async def _dup(db: Any, doc_id: Any) -> Any:
    return (await db.documents.find_one({"_id": doc_id}))["isDuplicate"]


async def _delete(client: Any, route: str, owner: Any, make_user: Any, doc_id: Any):
    if route == "user":
        return await client.delete(f"/api/documents/{doc_id}", headers=owner.headers)
    admin = await make_user(role="admin")
    return await client.delete(f"/api/admin/documents/{doc_id}", headers=admin.headers)


@pytest.mark.parametrize("route", ROUTES)
async def test_peer_clears_when_partner_edited_away(client, db, make_user, route) -> None:
    u = await make_user()
    a = await _doc(db, u, isDuplicate=True)
    b = await _doc(db, u, isDuplicate=True)
    await _patch(client, route, u, make_user, a, "receiptNumber", "UNIQ")
    assert await _dup(db, a) is False and await _dup(db, b) is False


@pytest.mark.parametrize("route", ROUTES)
async def test_peer_newly_flagged_when_edit_matches_it(client, db, make_user, route) -> None:
    u = await make_user()
    c = await _doc(db, u, receiptNumber="P7")
    b = await _doc(db, u, receiptNumber="P9")
    await _patch(client, route, u, make_user, b, "receiptNumber", "P7")
    assert await _dup(db, b) is True and await _dup(db, c) is True


@pytest.mark.parametrize("route", ROUTES)
async def test_peer_cleared_on_delete(client, db, make_user, route) -> None:
    u = await make_user()
    a = await _doc(db, u, isDuplicate=True)
    b = await _doc(db, u, isDuplicate=True)
    r = await _delete(client, route, u, make_user, a)
    assert r.status_code == 200
    assert await _dup(db, b) is False


@pytest.mark.parametrize("route", ROUTES)
async def test_three_way_remaining_pair_stays_duplicate(client, db, make_user, route) -> None:
    u = await make_user()
    a = await _doc(db, u, isDuplicate=True)
    b = await _doc(db, u, isDuplicate=True)
    c = await _doc(db, u, isDuplicate=True)
    await _patch(client, route, u, make_user, a, "receiptNumber", "UNIQ")
    assert [await _dup(db, x) for x in (a, b, c)] == [False, True, True]


@pytest.mark.parametrize("route", ROUTES)
async def test_peer_refresh_never_crosses_users(client, db, make_user, route) -> None:
    u1, u2 = await make_user(), await make_user()
    a = await _doc(db, u1)
    x = await _doc(db, u2, isDuplicate=True)  # deliberately stale/odd, must stay untouched
    y = await _doc(db, u2, isDuplicate=False)
    await _patch(client, route, u1, make_user, a, "receiptNumber", "ZZ")
    assert await _dup(db, x) is True and await _dup(db, y) is False
    await _delete(client, route, u1, make_user, a)
    assert await _dup(db, x) is True and await _dup(db, y) is False


async def test_user_and_admin_peer_results_match(client, db, make_user) -> None:
    out = {}
    for route in ROUTES:
        u = await make_user()
        a = await _doc(db, u, isDuplicate=True)
        b = await _doc(db, u, isDuplicate=True)
        c = await _doc(db, u, isDuplicate=True)
        await _patch(client, route, u, make_user, a, "date", "01/01/2024")
        out[route] = [await _dup(db, x) for x in (a, b, c)]
        await _delete(client, route, u, make_user, b)
        out[route] += [await _dup(db, c)]
    assert out["user"] == out["admin"] == [False, True, True, False]
