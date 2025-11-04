import json
from pathlib import Path
from typing import Iterator

import pytest

from buggy_auth import AuthService, authenticate


FIXTURE_DIR = Path(__file__).resolve().parent


def load_sample(index: int) -> dict:
    data_path = FIXTURE_DIR / "input_data.json"
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)[index]["input"]


@pytest.fixture()
def service() -> Iterator[AuthService]:
    svc = AuthService()
    yield svc
    svc.reset_state()


def test_valid_credentials(service: AuthService) -> None:
    result = service.authenticate(load_sample(0))
    assert result["status"] == "success"


def test_password_must_be_case_sensitive(service: AuthService) -> None:
    response = service.authenticate(load_sample(1))
    assert response["status"] == "failure"
    assert "Invalid credentials" in response["message"]


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


def test_rejects_non_mapping_payload() -> None:
    response = authenticate(["alice", "SecurePass123"])
    assert response["status"] == "failure"
    assert "payload" in response["message"].lower()
