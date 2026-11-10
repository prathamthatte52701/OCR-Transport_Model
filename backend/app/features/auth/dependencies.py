from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_database
from app.core.security import decode_token

_bearer_scheme = HTTPBearer(auto_error=False)

# The one user status: every account is active from signup.
STATUS_APPROVED = "approved"


def iso_utc(value: Any) -> str | None:
    """A stored datetime as an ISO-8601 UTC string ("...Z"); None for anything else.
    Mongo hands back naive datetimes, which are UTC by construction."""
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class CurrentUser:
    def __init__(self, id: ObjectId, role: str, must_change_password: bool = False):
        self.id = id
        self.role = role
        self.must_change_password = must_change_password


PASSWORD_CHANGE_REQUIRED = {
    "code": "PASSWORD_CHANGE_REQUIRED",
    "message": "You must set a new password before continuing.",
}


async def _authenticate(credentials: HTTPAuthorizationCredentials | None) -> CurrentUser:
    """FastAPI equivalent of the old requireAuth middleware: verifies the JWT,
    then re-reads tokenVersion from the DB and rejects if it no longer
    matches - this is the session-revocation check (password change /
    soft-delete invalidate every previously-issued token even before natural
    expiry)."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session. Please log in again.",
    )
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in to continue."
        )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise unauthorized

    try:
        user_id = ObjectId(payload.get("userId"))
    except (InvalidId, TypeError):
        raise unauthorized from None

    db = get_database()
    user = await db.users.find_one(
        {"_id": user_id},
        {
            "tokenVersion": 1,
            "role": 1,
            "mustChangePassword": 1,
        },
    )
    if user is None or user.get("tokenVersion") != payload.get("tokenVersion"):
        raise unauthorized

    return CurrentUser(
        id=user_id, role=user["role"], must_change_password=user.get("mustChangePassword") is True
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """Every protected route. Also the single enforcement point of the forced password
    change: a user holding an admin-set temporary password gets 403 PASSWORD_CHANGE_REQUIRED
    everywhere (require_admin included) except the two routes that use the variant below."""
    user = await _authenticate(credentials)
    if user.must_change_password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=PASSWORD_CHANGE_REQUIRED)
    return user


async def get_current_user_allow_password_change(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """Same checks, but lets a flagged user through. ONLY GET /auth/me and
    POST /auth/change-password may depend on this."""
    return await _authenticate(credentials)


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """FastAPI equivalent of the old isAdmin middleware: always re-reads role
    from the DB (never trusts the JWT's role claim, which is client-tamperable) -
    get_current_user above already did that DB read, so this just checks it."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user
