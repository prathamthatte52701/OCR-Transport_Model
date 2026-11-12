"""The end-of-session test-DB drop: the guard refuses anything that is not a plain test name."""

import pytest

from conftest import SESSION_TEST_DB, drop_session_db, safe_to_drop

REAL = "docintel_transport"


@pytest.mark.parametrize(
    "name",
    [
        "docintel_transport",
        "docintel_transport_x",
        "admin",
        "local",
        "config",
        "",
        "x",
        "_test",
        "docintel_transport_test_backup",
        "docintel test_test",
        "a/b_test",
        "a.b_test",
        "a b_test",
        "docintel_transport_test\n",
        "admin_test/..",
        None,
        5,
    ],
)
def test_refused_names(name: object) -> None:
    assert safe_to_drop(name, REAL) is False


def test_accepted_and_real_name_variants() -> None:
    assert safe_to_drop("docintel_transport_test", REAL) is True
    assert safe_to_drop("docintel_transport_p21a_test", REAL) is True
    # another app's test database on the same cluster is never ours to drop
    assert safe_to_drop("other_app_test", REAL) is False
    assert safe_to_drop("billing_test", REAL) is False
    assert safe_to_drop("test", REAL) is False
    # a "real" DB that itself looks like a test name is still refused
    assert safe_to_drop("docintel_transport_test", "docintel_transport_TEST") is False
    # I8: the old ACKN project names must never be droppable from here
    assert safe_to_drop("ackn_AI_model_test", REAL) is False  # historical name, now refused
    assert safe_to_drop("ackn_p21a_test", REAL) is False
    assert safe_to_drop("docintel_transport_test", None) is False


def test_session_name_passes_the_guard() -> None:
    assert safe_to_drop(SESSION_TEST_DB, REAL) is True


def test_hook_drops_only_when_everything_agrees(monkeypatch: pytest.MonkeyPatch) -> None:
    dropped: list[str] = []
    monkeypatch.setenv("MONGO_DB_NAME", "docintel_transport_x_test")
    assert drop_session_db("docintel_transport_x_test", "docintel_transport_x_test", REAL, dropped.append) is True
    assert dropped == ["docintel_transport_x_test"]


@pytest.mark.parametrize(
    "env, current, expected",
    [
        ("docintel_transport", "docintel_transport", "docintel_transport"),  # real, not a test name
        ("docintel_transport_x_test", "docintel_transport", "docintel_transport_x_test"),  # live setting is the real DB
        ("docintel_transport", "docintel_transport_x_test", "docintel_transport_x_test"),  # environment drifted
        ("docintel_transport_y_test", "docintel_transport_x_test", "docintel_transport_x_test"),  # environment names another DB
        ("admin", "admin", "admin"),
    ],
)
def test_hook_does_not_drop_when_ambiguous(
    monkeypatch: pytest.MonkeyPatch, env: str, current: str, expected: str
) -> None:
    dropped: list[str] = []
    monkeypatch.setenv("MONGO_DB_NAME", env)
    assert drop_session_db(expected, current, REAL, dropped.append) is False
    assert dropped == []
