import pytest

from fixed_auth import AuthService


@pytest.fixture()
def service():
    users = [
        {"username": "alice", "password": "SecurePass123"},
        {"username": "bob", "password": "PlainText!456"},
    ]
    return AuthService(users, max_attempts=3, lockout_seconds=1, iteration_count=80_000)


def test_valid_login(service):
    result = service.authenticate("alice", "SecurePass123", client_id="device-1")
    assert result["status"] == "success"
    assert result["message"] == "Login successful."
    assert result["attempts_left"] == 3


def test_wrong_case_password_fails(service):
    result = service.authenticate("alice", "securepass123", client_id="device-1")
    assert result["status"] == "failure"
    assert result["message"] == "Invalid credentials."
    assert result["attempts_left"] == 2


def test_non_string_password_rejected(service):
    result = service.authenticate("bob", 12345, client_id="device-2")
    assert result["status"] == "failure"
    assert "string" in result["message"].lower()
    assert result["attempts_left"] == 2


def test_unknown_user_rate_limits(service):
    for attempt in range(3):
        service.authenticate("mallory", "doesnotmatter", client_id="device-3")
    locked = service.authenticate("mallory", "doesnotmatter", client_id="device-3")
    assert locked["status"] == "failure"
    assert "Too many attempts" in locked["message"]
    assert locked["attempts_left"] == 0


def test_success_resets_attempts():
    users = [
        {"username": "alice", "password": "SecurePass123"},
        {"username": "bob", "password": "PlainText!456"},
    ]
    service = AuthService(users, max_attempts=2, lockout_seconds=0, iteration_count=80_000)
    service.authenticate("alice", "wrong", client_id="device-5")
    failure = service.authenticate("alice", "wrong", client_id="device-5")
    assert failure["attempts_left"] == 0
    success = service.authenticate("alice", "SecurePass123", client_id="device-5")
    assert success["status"] == "success"
    assert success["attempts_left"] == 2
