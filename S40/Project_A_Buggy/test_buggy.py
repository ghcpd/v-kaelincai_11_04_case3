import json
from pathlib import Path

import pytest

from buggy_auth import AuthService


@pytest.fixture()
def sample_data():
    path = Path(__file__).with_name("input_data.json")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture()
def service(sample_data):
    return AuthService(sample_data["users"], max_attempts=3, lockout_seconds=1)


def test_valid_login_succeeds(service, sample_data):
    scenario = sample_data["scenarios"]["valid_login"]
    result = service.authenticate(**scenario["input"])
    assert result == scenario["expected"]


def test_case_sensitive_password_should_fail(service, sample_data):
    """Expose the bug that lowercases passwords before hashing."""
    scenario = sample_data["scenarios"]["case_sensitive_login"]
    result = service.authenticate(**scenario["input"])
    # Expected behavior: status failure because the password casing differs.
    assert result == scenario["expected"], (
        "Bug reproduced: authentication succeeded even though the password "
        "differed by case."
    )


def test_non_string_password_rejected(service, sample_data):
    scenario = sample_data["scenarios"]["non_string_password"]
    result = service.authenticate(**scenario["input"])
    assert result == scenario["expected"]


def test_unknown_user_fails(service, sample_data):
    scenario = sample_data["scenarios"]["unknown_user"]
    result = service.authenticate(**scenario["input"])
    assert result == scenario["expected"]
