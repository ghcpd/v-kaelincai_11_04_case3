import time

import pytest

from fixed_auth import AuthenticationError, authenticate, format_result, get_default_store


def test_successful_login_exact_match():
    store = get_default_store()
    result = authenticate({"username": "alice", "password": "SecurePass123!"}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "success"
    assert sanitized["attempts_remaining"] == store["alice"].max_attempts


def test_password_with_trailing_whitespace_is_rejected():
    store = get_default_store()
    result = authenticate({"username": "alice", "password": "SecurePass123! "}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "failure"


def test_password_case_sensitivity_enforced():
    store = get_default_store()
    result = authenticate({"username": "alice", "password": "securepass123!"}, store)
    sanitized = format_result(result)
    assert sanitized["status"] == "failure"


def test_rate_limit_triggers_lock_and_cooldown():
    store = get_default_store()
    record = store["charlie"]
    for _ in range(record.max_attempts):
        authenticate({"username": "charlie", "password": "invalid"}, store)
    locked = authenticate({"username": "charlie", "password": "invalid"}, store)
    sanitized = format_result(locked)
    assert sanitized["status"] == "failure"
    assert sanitized.get("locked") is True
    assert record.is_locked is True
    assert record.lock_expires_at is not None


def test_non_string_payload_rejected():
    store = get_default_store()
    with pytest.raises(AuthenticationError):
        authenticate({"username": "alice", "password": 12345}, store)


def test_timestamp_removed_by_formatter():
    store = get_default_store()
    result = authenticate({"username": "bob", "password": "WinterMute2024"}, store)
    sanitized = format_result(result)
    assert "timestamp" not in sanitized
