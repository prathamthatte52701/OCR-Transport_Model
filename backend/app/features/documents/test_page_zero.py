"""I14: GET /documents?page=0 must stay in paged mode (clamped to page 1), never fall into the
legacy unbounded full-list mode that only applies when ?page= is absent entirely.

I15: needsReview=true must also match isDuplicate and a processed document missing a core
identifying field, not just the *NeedsReview flags."""

from datetime import UTC, datetime
from typing import Any


async def _insert_many(db: Any, owner: Any, n: int) -> None:
    now = datetime.now(UTC)
    docs = [
        {
            "userId": owner.id,
            "originalFilename": f"f{i}.pdf",
            "uploadStatus": "processed",
            "isDeleted": False,
            "createdAt": now,
            "updatedAt": now,
        }
        for i in range(n)
    ]
    await db.documents.insert_many(docs)


async def test_page_zero_is_paged_not_unbounded(client: Any, db: Any, make_user: Any) -> None:
    user = await make_user()
    await _insert_many(db, user, 5)
    res = await client.get(
        "/api/documents", headers=user.headers, params={"page": 0, "limit": 2}
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert "totalPages" in body and "currentPage" in body  # paged-mode shape, not the legacy list
    assert body["currentPage"] == 1  # clamped, not treated as "no page"
    assert len(body["documents"]) == 2


async def test_needs_review_matches_duplicate_flag(client: Any, db: Any, make_user: Any) -> None:
    user = await make_user()
    now = datetime.now(UTC)
    await db.documents.insert_many(
        [
            {
                "userId": user.id,
                "originalFilename": "dup.pdf",
                "uploadStatus": "processed",
                "isDeleted": False,
                "isDuplicate": True,
                "receiptNumber": "X1",
                "date": "01/01/2026",
                "totalAmount": "100",
                "createdAt": now,
                "updatedAt": now,
            },
            {
                "userId": user.id,
                "originalFilename": "clean.pdf",
                "uploadStatus": "processed",
                "isDeleted": False,
                "receiptNumber": "X2",
                "date": "01/01/2026",
                "totalAmount": "200",
                "createdAt": now,
                "updatedAt": now,
            },
        ]
    )
    res = await client.get("/api/documents", headers=user.headers, params={"needsReview": True})
    assert res.status_code == 200, res.text
    names = {d["originalFilename"] for d in res.json()["documents"]}
    assert names == {"dup.pdf"}


async def test_needs_review_matches_missing_core_field_on_processed_doc(
    client: Any, db: Any, make_user: Any
) -> None:
    user = await make_user()
    now = datetime.now(UTC)
    await db.documents.insert_many(
        [
            {
                "userId": user.id,
                "originalFilename": "missing_total.pdf",
                "uploadStatus": "processed",
                "isDeleted": False,
                "receiptNumber": "X3",
                "date": "01/01/2026",
                "totalAmount": "",
                "createdAt": now,
                "updatedAt": now,
            },
            {
                "userId": user.id,
                "originalFilename": "clean2.pdf",
                "uploadStatus": "processed",
                "isDeleted": False,
                "receiptNumber": "X4",
                "date": "01/01/2026",
                "totalAmount": "300",
                "createdAt": now,
                "updatedAt": now,
            },
        ]
    )
    res = await client.get("/api/documents", headers=user.headers, params={"needsReview": True})
    assert res.status_code == 200, res.text
    names = {d["originalFilename"] for d in res.json()["documents"]}
    assert names == {"missing_total.pdf"}
