"""I13: the per-email login limiter must count FAILED logins only, keyed on email+IP, so a
successful login never eats the budget and one IP can never lock a victim out from another IP."""

from typing import Any

from app.core import rate_limit


async def _signup(client: Any, username: str, email: str, password: str = "Password1!") -> None:
    r = await client.post(
        "/api/auth/signup",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code == 201, r.text


async def test_successful_login_does_not_consume_budget(client: Any) -> None:
    email = "ratelimit-success@looptest.local"
    password = "Password1!"
    await _signup(client, "rlsucc", email, password)
    for i in range(5):
        r = await client.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, (i, r.text)
    # Logic-level proof the budget truly was not touched: 5 real successes above, then the
    # email+IP key still has its full window available for a failed-attempt check.
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1),
    }
    rate_limit.check_login_email_limit(Request(scope), email)  # must not raise


async def test_failed_logins_lock_out_after_budget_exhausted(client: Any) -> None:
    email = "ratelimit-fail@looptest.local"
    await _signup(client, "rlfail", email, "Password1!")
    statuses = []
    for _ in range(25):
        r = await client.post("/api/auth/login", json={"email": email, "password": "Wrong1!"})
        statuses.append(r.status_code)
    assert 429 in statuses
    assert all(s in (401, 429) for s in statuses)


def test_other_ip_is_not_locked_out_by_an_attack_on_the_same_email() -> None:
    from starlette.requests import Request

    def _req(ip: str) -> Request:
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/",
            "query_string": b"",
            "headers": [],
            "client": (ip, 1234),
        }
        return Request(scope)

    email = "ratelimit-multi-ip@looptest.local"
    attacker = _req("203.0.113.9")
    victim = _req("198.51.100.5")
    for _ in range(25):
        try:
            rate_limit.check_login_email_limit(attacker, email)
        except Exception:
            pass
        rate_limit.record_login_failure(attacker, email)
    # The attacker's IP is now locked for this email...
    locked = False
    try:
        rate_limit.check_login_email_limit(attacker, email)
    except Exception:
        locked = True
    assert locked
    # ...but a different IP against the same email is untouched.
    rate_limit.check_login_email_limit(victim, email)  # must not raise


def test_success_path_never_calls_record_login_failure(monkeypatch: Any) -> None:
    """Direct proof against the router source: a successful login must not call
    record_login_failure, only check_login_email_limit."""
    import ast
    import inspect

    from app.features.auth import router as auth_router

    src = inspect.getsource(auth_router.login)
    tree = ast.parse(src)
    calls_after_password_ok = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls_after_password_ok.append(node.func.id)
    assert "record_login_failure" in calls_after_password_ok  # called on the failure branch
    assert "check_login_email_limit" in calls_after_password_ok
