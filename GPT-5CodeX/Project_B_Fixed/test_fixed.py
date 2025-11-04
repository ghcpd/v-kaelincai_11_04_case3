import pytest
from typing import Iterator

from fixed_auth import AuthService, authenticate


@pytest.fixture()
def service() -> Iterator[AuthService]:
    svc = AuthService()
    yield svc
    svc.reset_state()


def test_valid_credentials(service: AuthService) -> None:
    result = service.authenticate({"username": "alice", "password": "SecurePass123"})
    assert result["status"] == "success"


def test_password_is_case_sensitive(service: AuthService) -> None:
    response = service.authenticate({"username": "alice", "password": "securepass123"})
    assert response["status"] == "failure"
    assert "invalid credentials" in response["message"].lower()


def test_missing_password_is_rejected(service: AuthService) -> None:
    result = service.authenticate({"username": "bob", "password": ""})
    assert result["status"] == "failure"
    assert "required" in result["message"].lower()


def test_account_locks_after_max_attempts(service: AuthService) -> None:
    for _ in range(service.MAX_FAILED_ATTEMPTS):
        service.authenticate({"username": "bob", "password": "wrong"})

    lock_response = service.authenticate({"username": "bob", "password": "wrong"})
    assert lock_response["status"] == "failure"
    assert "locked" in lock_response["message"].lower()


def test_non_string_payload_is_rejected(service: AuthService) -> None:
    result = service.authenticate({"username": "alice", "password": 12345})
    assert result["status"] == "failure"
    assert "must be strings" in result["message"].lower()


def test_module_level_authenticate_wrapper() -> None:
    result = authenticate({"username": "alice", "password": "SecurePass123"})
    assert result["status"] == "success"
