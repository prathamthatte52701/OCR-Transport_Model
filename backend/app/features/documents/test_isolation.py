"""T10: two-user IDOR sweep over every documents/ route that takes an id or a list of
ids. User A is the attacker holding B's ids. Expected everywhere: 404 (or an empty/
skipped result), never B's data. Admin can still reach everything (with audit entries).

Route -> where the userId scope applies (verified by reading the code):
  GET    /documents                       list filter {"userId": caller}
  GET    /documents/training-stats        base_filter userId
  GET    /documents/my-activity           auditlogs filter userId + doc lookup userId
  GET    /documents/{id}                  _get_owned_document(userId)
  GET    /documents/{id}/download         _get_owned_document(userId)
  POST   /documents/download-all          per-id find_one userId (others skipped)
  POST   /documents/{id}/reprocess        _get_owned_document(userId)
  DELETE /documents/{id}                  _get_owned_document(userId)
  POST   /documents/{id}/purge-file       _get_owned_document(userId)
  PATCH  /documents/{id}/correct          _get_owned_document(userId)
"""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from app.features.documents.gridfs_service import upload_buffer


async def _doc(db: Any, owner: Any, number: str = "820000001") -> ObjectId:
    now = datetime.now(UTC)
    file_id = await upload_buffer(b"%PDF-1.4 fake", "x.pdf", "application/pdf")
    res = await db.documents.insert_one(
        {
            "userId": owner.id,
            "autoName": "n",
            "originalFilename": "x.pdf",
            "mimeType": "application/pdf",
            "size": 13,
            "uploadStatus": "processed",
            "receiptNumber": number,
            "date": "01/01/2026",
            "gridFsFileId": file_id,
            "edited": False,
            "isDeleted": False,
            "filePurged": False,
            "createdAt": now,
            "updatedAt": now,
        }
    )
    return res.inserted_id


async def test_idor_every_id_route_returns_404_for_other_users_document(
    client: Any, db: Any, make_user: Any
) -> None:
    a, b = await make_user(), await make_user()
    b_doc = await _doc(db, b)
    h = a.headers

    assert (await client.get(f"/api/documents/{b_doc}", headers=h)).status_code == 404
    assert (await client.get(f"/api/documents/{b_doc}/download", headers=h)).status_code == 404
    assert (await client.post(f"/api/documents/{b_doc}/reprocess", headers=h)).status_code == 404
    assert (await client.post(f"/api/documents/{b_doc}/purge-file", headers=h)).status_code == 404
    r = await client.patch(
        f"/api/documents/{b_doc}/correct", headers=h, json={"field": "receiptNumber", "value": "820999999"}
    )
    assert r.status_code == 404
    assert (await client.delete(f"/api/documents/{b_doc}", headers=h)).status_code == 404

    # B's document is completely untouched
    doc = await db.documents.find_one({"_id": b_doc})
    assert doc["receiptNumber"] == "820000001" and not doc["isDeleted"] and not doc["filePurged"]
    assert await db.corrections.count_documents({}) == 0


async def test_idor_lists_and_stats_never_include_other_users_data(
    client: Any, db: Any, make_user: Any
) -> None:
    a, b = await make_user(), await make_user()
    await _doc(db, b, "820000077")
    for path in (
        "/api/documents",
        "/api/documents?page=1&limit=100",
        "/api/documents?number=820000077",
        "/api/documents/my-activity",
    ):
        r = await client.get(path, headers=a.headers)
        assert r.status_code == 200, path
        assert "820000077" not in r.text and str(b.id) not in r.text, path
    stats = (await client.get("/api/documents/training-stats", headers=a.headers)).json()
    assert stats == {"trainedCount": 0, "correctedCount": 0}


async def test_idor_download_all_skips_foreign_ids(client: Any, db: Any, make_user: Any) -> None:
    a, b = await make_user(), await make_user()
    b_doc = await _doc(db, b)
    r = await client.post(
        "/api/documents/download-all", headers=a.headers, json={"documentIds": [str(b_doc)]}
    )
    # nothing of B's can be zipped: either nothing to download, or an empty bundle
    assert r.headers.get("x-download-included", "0") == "0"
    assert b"%PDF" not in r.content


async def test_admin_reaches_everything_with_audit(client: Any, db: Any, make_user: Any) -> None:
    admin, b = await make_user(role="admin"), await make_user()
    b_doc = await _doc(db, b)
    r = await client.get(f"/api/admin/documents?userId={b.id}", headers=admin.headers)
    assert r.status_code == 200 and str(b_doc) in r.text
    assert await db.auditlogs.count_documents({"action": "admin_access"}) == 1
