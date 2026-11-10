"""T8: every admin route that opens/lists another user's data writes
an audit entry (adminId, targetUserId, resource, action, time)."""

from typing import Any


async def _entries(db: Any) -> list[dict[str, Any]]:
    return [e async for e in db.auditlogs.find({"action": "admin_access"})]


async def test_admin_list_documents_is_audited(client: Any, db: Any, make_user: Any) -> None:
    admin = await make_user(role="admin")
    owner = await make_user()
    r = await client.get(f"/api/admin/documents?userId={owner.id}", headers=admin.headers)
    assert r.status_code == 200
    r = await client.get("/api/admin/documents", headers=admin.headers)
    assert r.status_code == 200
    entries = await _entries(db)
    assert len(entries) == 2
    targeted = [e for e in entries if e["context"]["targetUserId"] == str(owner.id)]
    assert len(targeted) == 1
    ctx = targeted[0]["context"]
    assert ctx["adminId"] == str(admin.id) and ctx["resource"] == "documents"
    assert ctx["action"] == "list" and targeted[0]["createdAt"]
    assert targeted[0]["userId"] == admin.id
    assert any(e["context"]["targetUserId"] is None for e in entries)  # all-users view


async def test_admin_viewing_own_data_not_logged(client: Any, db: Any, make_user: Any) -> None:
    admin = await make_user(role="admin")
    await client.get(f"/api/admin/documents?userId={admin.id}", headers=admin.headers)
    assert await _entries(db) == []


async def test_non_admin_cannot_trigger_admin_routes_or_audit(
    client: Any, db: Any, make_user: Any
) -> None:
    user = await make_user()
    assert (await client.get("/api/admin/documents", headers=user.headers)).status_code == 403
    assert await _entries(db) == []
