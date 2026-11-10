"""GET /documents?page=&sort=&order=: whitelist, correct orderings, stable paging."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

SORT_KEYS = ["number", "date", "uploadStatus", "edited", "createdAt"]
BASE = datetime(2026, 1, 1, tzinfo=UTC)


def _display_number(d: dict[str, Any]) -> str:
    return d.get("receiptNumber") or ""


def _date_key(d: dict[str, Any]) -> str:
    v = d.get("date")
    if isinstance(v, str) and len(v) == 10 and v[2] == "/" and v[5] == "/":
        dd, mm, yy = v[:2], v[3:5], v[6:]
        if (dd + mm + yy).isdigit():
            return yy + mm + dd
    return ""


def _key(sort: str, d: dict[str, Any]) -> Any:
    if sort == "uploadStatus":
        return d[sort].lower()
    if sort == "edited":
        return bool(d.get("edited"))
    if sort == "number":
        return _display_number(d).lower()
    if sort == "date":
        return _date_key(d)
    return d["createdAt"]


def _doc(owner: Any, n: int, **kw: Any) -> dict[str, Any]:
    t = BASE + timedelta(seconds=n)
    d: dict[str, Any] = {
        "userId": owner.id,
        "originalFilename": f"f{n}.pdf",
        "uploadStatus": "processed",
        "edited": False,
        "isDeleted": False,
        "createdAt": t,
        "updatedAt": t,
    }
    d.update(kw)
    for k in [k for k, v in d.items() if isinstance(v, str) and v == "UNSET"]:
        del d[k]
    return d


async def _walk(client: Any, user: Any, limit: int = 7, **params: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        res = await client.get(
            "/api/documents",
            headers=user.headers,
            params={"page": page, "limit": limit, **params},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        out += body["documents"]
        if page >= body["totalPages"]:
            return out
        page += 1


def _check_order(
    sort: str, order: str, got: list[dict[str, Any]], docs: list[dict[str, Any]]
) -> None:
    ids = [d["_id"] for d in got]
    assert len(ids) == len(set(ids)) == len(docs)
    assert set(ids) == {str(d["_id"]) for d in docs}
    by_id = {str(d["_id"]): d for d in docs}
    keys = [_key(sort, by_id[i]) for i in ids]
    assert keys == sorted(keys, reverse=order == "desc")


@pytest.fixture
async def mixed(db: Any, make_user: Any) -> Any:
    u, other = await make_user(), await make_user()
    docs = [
        _doc(u, 1, receiptNumber="G0027704827"),
        _doc(u, 2, receiptNumber="A100"),
        _doc(u, 3, receiptNumber="a100"),
        _doc(u, 4),
        _doc(u, 5, receiptNumber="B200", date="01/02/2026", uploadStatus="uploaded"),
        _doc(u, 6, receiptNumber="C300", date="15/01/2026", edited=True, uploadStatus="failed"),
        _doc(u, 7, receiptNumber="A050", date="31/12/2025", edited="UNSET"),
        _doc(u, 8, receiptNumber=None, date="05/03/2025"),
        _doc(u, 9),  # number and date missing
        _doc(u, 10, receiptNumber="Z9", date=None),
        _doc(u, 11, receiptNumber="Y9", date=""),
        _doc(u, 12, receiptNumber="X9", date="2026-01-05"),
        _doc(u, 13, receiptNumber="W9", date="abc"),
        _doc(u, 14, receiptNumber="V9", date="5/1/2026"),
        _doc(u, 15, receiptNumber="M1", date="10/10/2026", edited=True),
    ]
    await db.documents.insert_many(docs)
    await db.documents.insert_many(
        [_doc(other, 100 + i, receiptNumber=f"OTHER{i}", date="01/01/2020") for i in range(5)]
    )
    return u, docs


@pytest.mark.parametrize("order", ["asc", "desc"])
@pytest.mark.parametrize("sort", SORT_KEYS)
async def test_sort_matches_bruteforce(client: Any, mixed: Any, sort: str, order: str) -> None:
    u, docs = mixed
    got = await _walk(client, u, sort=sort, order=order)
    _check_order(sort, order, got, docs)


async def test_default_is_created_at_desc(client: Any, mixed: Any) -> None:
    u, docs = mixed
    got = await _walk(client, u)
    assert [d["_id"] for d in got] == [
        str(d["_id"]) for d in sorted(docs, key=lambda d: d["createdAt"], reverse=True)
    ]


async def test_date_chronological_and_empty_group_position(client: Any, mixed: Any) -> None:
    u, docs = mixed
    by_id = {str(d["_id"]): d for d in docs}
    asc = [_date_key(by_id[d["_id"]]) for d in await _walk(client, u, sort="date", order="asc")]
    desc = [_date_key(by_id[d["_id"]]) for d in await _walk(client, u, sort="date", order="desc")]
    empties = sum(k == "" for k in asc)
    assert empties >= 8
    assert asc[:empties] == [""] * empties
    assert desc[-empties:] == [""] * empties
    assert [k for k in asc if k][:4] == ["20250305", "20251231", "20260115", "20260201"]


async def test_number_sorts_by_receipt_number(client: Any, mixed: Any) -> None:
    u, docs = mixed
    got = await _walk(client, u, sort="number", order="asc")
    by_id = {str(d["_id"]): d for d in docs}
    shown = [_display_number(by_id[d["_id"]]).lower() for d in got]
    assert "g0027704827" in shown
    assert shown == sorted(shown)


async def test_case_only_differences_group_together(client: Any, db: Any, make_user: Any) -> None:
    u = await make_user()
    vals = ["Alpha", "alpha", "ALPHA", "beta", "Beta", "alPHa", "gamma"]
    await db.documents.insert_many([_doc(u, i, uploadStatus=v) for i, v in enumerate(vals)])
    for order in ("asc", "desc"):
        got = await _walk(client, u, sort="uploadStatus", order=order)
        low = [d["uploadStatus"].lower() for d in got]
        assert len(got) == len(vals)
        assert low == sorted(low, reverse=order == "desc")


@pytest.mark.parametrize("sort", ["uploadStatus", "date", "edited", "number"])
@pytest.mark.parametrize("order", ["asc", "desc"])
async def test_stable_paging_with_many_ties(
    client: Any, db: Any, make_user: Any, sort: str, order: str
) -> None:
    u = await make_user()
    statuses = ["uploaded", "processed", "failed"]
    dates = ["01/02/2026", "15/01/2026", "31/12/2025", "05/03/2025"]
    docs = [
        _doc(
            u,
            i,
            uploadStatus=statuses[i % 3],
            date=dates[i % 4],
            receiptNumber=f"N{i % 2}",
            edited=i % 2 == 0,
        )
        for i in range(45)
    ]
    await db.documents.insert_many(docs)
    paged = await _walk(client, u, limit=7, sort=sort, order=order)
    big = await _walk(client, u, limit=100, sort=sort, order=order)
    assert [d["_id"] for d in paged] == [d["_id"] for d in big]
    _check_order(sort, order, paged, docs)


async def test_sort_with_filters(client: Any, mixed: Any) -> None:
    u, docs = mixed
    a100 = [d for d in docs if "a100" in (d.get("receiptNumber") or "").lower()]
    got = await _walk(client, u, sort="number", order="desc", number="a100")
    _check_order("number", "desc", got, a100)
    res = await client.get(
        "/api/documents",
        headers=u.headers,
        params={"page": 1, "limit": 3, "sort": "date", "order": "asc", "number": "G0027704827"},
    )
    body = res.json()
    assert body["totalDocuments"] == 1 and len(body["documents"]) == 1
    assert body["totalPages"] == 1 and body["currentPage"] == 1


@pytest.mark.parametrize(
    "params",
    [
        {"sort": "passwordHash"},
        {"sort": "createdAt;drop"},
        {"sort": ""},
        {"sort": "createdAt", "order": "sideways"},
        {"order": "sideways"},
    ],
)
async def test_invalid_sort_or_order_rejected(client: Any, mixed: Any, params: dict) -> None:
    u, _ = mixed
    res = await client.get("/api/documents", headers=u.headers, params={"page": 1, **params})
    assert res.status_code == 422, res.text


async def test_sort_without_page_does_not_crash(client: Any, mixed: Any) -> None:
    u, _ = mixed
    res = await client.get("/api/documents", headers=u.headers, params={"sort": "date"})
    assert res.status_code == 200


async def test_caps(client: Any, mixed: Any) -> None:
    u, _ = mixed
    res = await client.get(
        "/api/documents", headers=u.headers, params={"page": 1, "limit": 100000, "sort": "date"}
    )
    assert res.status_code == 200 and len(res.json()["documents"]) <= 100
    res = await client.get(
        "/api/documents", headers=u.headers, params={"page": 10**18, "limit": 5, "sort": "date"}
    )
    assert res.status_code == 200


async def test_response_shape_and_no_leak(client: Any, mixed: Any) -> None:
    u, _ = mixed
    base = await _walk(client, u, limit=100)
    sorted_ = await _walk(client, u, limit=100, sort="number", order="asc")
    assert {d["_id"]: set(d) for d in base} == {d["_id"]: set(d) for d in sorted_}
    res = await client.get(
        "/api/documents", headers=u.headers, params={"page": 1, "limit": 5, "sort": "date"}
    )
    assert {"totalDocuments", "totalPages", "currentPage", "documents"} <= set(res.json())


async def test_auth_and_isolation(client: Any, mixed: Any) -> None:
    u, docs = mixed
    res = await client.get("/api/documents", params={"page": 1, "sort": "date"})
    assert res.status_code == 401
    for sort in SORT_KEYS:
        got = await _walk(client, u, sort=sort, order="asc")
        assert {d["userId"] for d in got} == {str(u.id)}
        assert len(got) == len(docs)
