import json
import pathlib
from typing import Dict

import pytest

from buggy_auth import authenticate, format_result, get_default_store


FIXTURE_DIR = pathlib.Path(__file__).parent


def load_input_cases() -> Dict[str, Dict[str, object]]:
    payloads = json.loads((FIXTURE_DIR / "input_data.json").read_text())
    return {case["description"]: case for case in payloads}


def test_successful_login_exact_match():
    store = get_default_store()
    result = authenticate({"username": "alice", "password": "SecurePass123!"}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "success"
    assert sanitized["attempts_remaining"] == store["alice"].max_attempts


def test_password_with_whitespace_should_fail():
    store = get_default_store()
    # The bug in buggy_auth.py normalizes passwords by stripping whitespace,
    # which incorrectly allows the login below to succeed. The expected
    # behavior is failure, so this assertion exposes the regression.
    result = authenticate({"username": "alice", "password": "SecurePass123! "}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "failure", "Whitespace-padded password must not authenticate"


@pytest.mark.parametrize(
    "username,password",
    [
        ("alice", "' OR '1'='1"),
        ("alice", "--comment"),
        ("bob", "bad"),
    ],
)
def test_malformed_passwords_are_blocked(username: str, password: str):
    store = get_default_store()
    result = authenticate({"username": username, "password": password}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "failure"
    assert sanitized.get("locked") in (None, False)


def test_rate_limit_triggers_lock_after_max_attempts():
    store = get_default_store()
    for _ in range(store["charlie"].max_attempts):
        authenticate({"username": "charlie", "password": "incorrect"}, store)
    result = authenticate({"username": "charlie", "password": "incorrect"}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "failure"
    assert sanitized.get("locked") is True
    assert store["charlie"].is_locked is True
