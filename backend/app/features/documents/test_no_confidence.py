"""The raw OCR text (ocrTextHidden) is stored for debugging but no API response may expose it."""

from datetime import UTC, datetime
from typing import Any

SECRET = "RAW-OCR-TEXT-SECRET"


async def test_list_get_and_correct_never_expose_ocr_text(
    client: Any, db: Any, make_user: Any
) -> None:
    u = await make_user()
    now = datetime.now(UTC)
    res = await db.documents.insert_one(
        {
            "userId": u.id,
            "autoName": "d",
            "originalFilename": "d.pdf",
            "mimeType": "application/pdf",
            "size": 1,
            "uploadStatus": "processed",
            "receiptNumber": "820000001",
            "date": "05/10/2026",
            "edited": False,
            "isDeleted": False,
            "filePurged": True,
            "ocrTextHidden": SECRET,
            "createdAt": now,
            "updatedAt": now,
        }
    )
    doc_id = res.inserted_id
    listing = await client.get("/api/documents", headers=u.headers)
    assert listing.status_code == 200 and SECRET not in listing.text
    one = await client.get(f"/api/documents/{doc_id}", headers=u.headers)
    assert one.status_code == 200 and SECRET not in one.text
    fixed = await client.patch(
        f"/api/documents/{doc_id}/correct",
        headers=u.headers,
        json={"field": "receiptNumber", "value": "820000002"},
    )
    assert fixed.status_code == 200, fixed.text
    assert SECRET not in fixed.text
    stored = await db.documents.find_one({"_id": doc_id})
    assert stored["receiptNumber"] == "820000002" and stored["edited"] is True
    assert stored["ocrTextHidden"] == SECRET  # not rewritten
