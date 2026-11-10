from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.audit_log import log_action
from app.core.database import get_database
from app.core.rate_limit import (
    allow_password_reset_for_email,
    enforce_login_email_limit,
    limiter,
)
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    sign_token,
    verify_password,
)
from app.core.validators import (
    normalize_email,
    normalize_username,
    validate_email,
    validate_password,
    validate_username,
)
from app.features.auth.dependencies import (
    STATUS_APPROVED,
    CurrentUser,
    get_current_user,
    get_current_user_allow_password_change,
)
from app.features.auth.password_requests import (
    GENERIC_RESET_MESSAGE,
    can_request_reset,
    handle_reset_request,
    sanitize_note,
)
from app.features.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    PasswordResetRequestBody,
    SignupRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserOut,
)

router = APIRouter()

# Shared text for every non-field-specific signup failure (duplicate email,
# race-condition duplicate) - must stay byte-identical so none of them stands
# out as the "email already exists" case in particular (account-enumeration fix).
GENERIC_SIGNUP_ERROR = "Could not create your account. Please check your details and try again."


def _user_out(user: dict) -> UserOut:
    return UserOut(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user["role"],
        must_change_password=user.get("mustChangePassword") is True,
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
@limiter.limit("15/hour")
async def signup(request: Request, body: SignupRequest) -> TokenResponse:
    db = get_database()

    email = normalize_email(body.email)
    username = normalize_username(body.username)

    if err := validate_username(username):
        raise HTTPException(status_code=400, detail=err)
    if err := validate_email(email):
        raise HTTPException(status_code=400, detail=err)
    if err := validate_password(body.password, username, email):
        raise HTTPException(status_code=400, detail=err)

    # Hash before the uniqueness check so a taken-email response costs
    # roughly the same as a successful signup - a response-time gap would
    # otherwise let an attacker use signup as an email-existence oracle.
    password_hash = hash_password(body.password)

    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail=GENERIC_SIGNUP_ERROR)

    now = datetime.now(UTC)
    try:
        await db.users.insert_one(
            {
                "username": username,
                "email": email,
                "passwordHash": password_hash,
                "role": "user",
                "status": STATUS_APPROVED,
                "tokenVersion": 0,
                "createdAt": now,
                "updatedAt": now,
            }
        )
    except Exception as exc:
        if "E11000" in str(exc):
            raise HTTPException(status_code=400, detail=GENERIC_SIGNUP_ERROR) from exc
        raise

    created = await db.users.find_one({"email": email})
    assert created is not None
    await log_action(created["_id"], "signup", {"email": email})
    # Active immediately: log the new user in right away (same token/user shape as /login).
    token = sign_token(str(created["_id"]), created["tokenVersion"], created["role"])
    return TokenResponse(token=token, user=_user_out(created))


@router.post("/password-reset-request", response_model=MessageResponse)
@limiter.limit("10/hour")
async def password_reset_request(
    request: Request, body: PasswordResetRequestBody
) -> MessageResponse:
    """Public. Always the same generic 200 (only the per-IP limit can answer 429); a request
    row is created only for a non-admin account with a password."""
    db = get_database()
    email = normalize_email(body.email)
    user = await db.users.find_one({"email": email})
    could_create = can_request_reset(user)
    within_limit = allow_password_reset_for_email(email) if could_create else True
    eligible = could_create and within_limit
    await handle_reset_request(db, user, sanitize_note(body.note), eligible)
    return MessageResponse(message=GENERIC_RESET_MESSAGE)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("100/15minute")
async def login(request: Request, body: LoginRequest) -> TokenResponse:
    db = get_database()
    email = normalize_email(body.email)
    if not email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    await enforce_login_email_limit(request, email)

    user = await db.users.find_one({"email": email})
    # Always run exactly one bcrypt check (against a dummy hash when there is no
    # usable password) so unknown email / passwordless account / wrong password
    # are indistinguishable in both response and timing.
    stored_hash = user.get("passwordHash") if user else None
    password_ok = verify_password(body.password, stored_hash or DUMMY_PASSWORD_HASH)
    if not user or not stored_hash or not password_ok:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    # Auto-close an open password-reset request: the user got in with their own password.
    # Skipped while a temporary password is in force (that request is already done). One
    # conditional update, so it is race-safe and a no-op when nothing is open.
    if user.get("mustChangePassword") is not True:
        now = datetime.now(UTC)
        await db.passwordresetrequests.update_one(
            {"userId": user["_id"], "status": "open"},
            {
                "$set": {
                    "status": "done",
                    "resolution": "user_logged_in",
                    "resolvedAt": now,
                    "resolvedBy": None,
                    "updatedAt": now,
                }
            },
        )

    token = sign_token(str(user["_id"]), user["tokenVersion"], user["role"])
    await log_action(user["_id"], "login", {"email": email})
    return TokenResponse(token=token, user=_user_out(user))


@router.get("/me", response_model=dict)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user_allow_password_change),
) -> dict:
    db = get_database()
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"user": _user_out(user)}


@router.patch("/me", response_model=dict)
async def update_me(
    body: UpdateProfileRequest, current_user: CurrentUser = Depends(get_current_user)
) -> dict:
    db = get_database()
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    updates: dict = {}
    if body.username is not None:
        username = normalize_username(body.username)
        if err := validate_username(username):
            raise HTTPException(status_code=400, detail=err)
        updates["username"] = username

    # Email is an identity anchor, so only an admin can change it. Sending
    # the unchanged address (the profile form does) is harmless and allowed.
    if body.email is not None and normalize_email(body.email) != user["email"]:
        raise HTTPException(
            status_code=403, detail="Only an admin can change your email. Contact the admin."
        )

    if updates:
        updates["updatedAt"] = datetime.now(UTC)
        await db.users.update_one({"_id": current_user.id}, {"$set": updates})
        refreshed = await db.users.find_one({"_id": current_user.id})
        assert refreshed is not None
        user = refreshed

    return {"user": _user_out(user)}


@router.post("/change-password", response_model=TokenResponse)
@limiter.limit("20/15minute")
async def change_password(
    request: Request,
    body: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user_allow_password_change),
) -> TokenResponse:
    if body.new_password != body.confirm_new_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match.")

    db = get_database()
    user = await db.users.find_one({"_id": current_user.id})
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    if "passwordHash" not in user:
        raise HTTPException(status_code=400, detail="This account has no password to change.")

    if not verify_password(body.current_password, user["passwordHash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    if body.new_password == body.current_password:
        raise HTTPException(
            status_code=400, detail="New password must be different from your current password."
        )
    if err := validate_password(body.new_password, user.get("username"), user.get("email")):
        raise HTTPException(status_code=400, detail=err)

    was_forced = user.get("mustChangePassword") is True
    new_hash = hash_password(body.new_password)
    new_token_version = user["tokenVersion"] + 1
    changes: dict = {
        "passwordHash": new_hash,
        "tokenVersion": new_token_version,
        "updatedAt": datetime.now(UTC),
    }
    if was_forced:
        changes["mustChangePassword"] = False
    # Conditional on the hash + tokenVersion we verified against: if an admin set a temp
    # password in between, that write wins and this one is refused instead of overwriting it.
    written = await db.users.update_one(
        {
            "_id": current_user.id,
            "passwordHash": user["passwordHash"],
            "tokenVersion": user["tokenVersion"],
        },
        {"$set": changes},
    )
    if written.matched_count == 0:
        raise HTTPException(
            status_code=409,
            detail="Your password was changed elsewhere. Please log in again.",
        )
    user["passwordHash"] = new_hash
    user["tokenVersion"] = new_token_version
    user["mustChangePassword"] = False

    # Re-issue a fresh token carrying the new tokenVersion so the tab that
    # just changed the password doesn't get logged out too - only every
    # OTHER previously-issued token is now invalid.
    token = sign_token(str(user["_id"]), new_token_version, user["role"])
    await log_action(user["_id"], "password_change", {"method": "change_password"})
    if was_forced:
        # A request filed between the temp password and this change would otherwise stay open.
        closed_at = datetime.now(UTC)
        await db.passwordresetrequests.update_one(
            {"userId": user["_id"], "status": "open"},
            {
                "$set": {
                    "status": "done",
                    "resolution": "user_logged_in",
                    "resolvedAt": closed_at,
                    "updatedAt": closed_at,
                    "resolvedBy": None,
                }
            },
        )
        await log_action(user["_id"], "PASSWORD_CHANGED_FORCED", {})
    return TokenResponse(token=token, user=_user_out(user))
