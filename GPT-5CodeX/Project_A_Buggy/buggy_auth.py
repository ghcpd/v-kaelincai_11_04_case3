"""Deliberately buggy authentication service used for functional bug reproduction tests."""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict


class AuthService:
    """Simplified auth service with intentional logic defects for testing."""

    MAX_FAILED_ATTEMPTS = 3

    def __init__(self) -> None:
        self._bootstrap_users()

    def _bootstrap_users(self) -> None:
        self.users: Dict[str, Dict[str, Any]] = {
            "alice": {
                "password_hash": self._hash_password("SecurePass123"),
                "failed_attempts": 0,
                "last_login": None,
            },
            "bob": {
                "password_hash": self._hash_password("Tr1cky!Pass"),
                "failed_attempts": 0,
                "last_login": None,
            },
        }

    def reset_state(self) -> None:
        """Reset in-memory state between tests."""
        self._bootstrap_users()

    def _hash_password(self, password: Any) -> str:
        """Return a SHA-256 hash of the provided password.

        BUG: Converts the password to lowercase before hashing, which removes
        case-sensitivity from credential validation and allows incorrect
        passwords that only differ by case to authenticate successfully.
        """

        if not isinstance(password, str):
            password = str(password)
        normalized = password.lower()  # BUG: forces lowercase
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def authenticate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {
                "status": "failure",
                "message": "Invalid request payload.",
            }

        username = (payload.get("username") or "").strip()
        password = payload.get("password", "")

        if not username or not password:
            return {
                "status": "failure",
                "message": "Username and password are required.",
            }

        user = self.users.get(username)
        if not user:
            return {
                "status": "failure",
                "message": "Invalid credentials.",
            }

        if user["failed_attempts"] > self.MAX_FAILED_ATTEMPTS:
            return {
                "status": "failure",
                "message": "Account locked due to too many failed attempts.",
            }

        incoming_hash = self._hash_password(password)
        if incoming_hash == user["password_hash"]:
            user["failed_attempts"] = 0
            user["last_login"] = time.time()
            return {
                "status": "success",
                "message": "Login successful.",
            }

        # BUG: lock threshold check above allows one extra attempt before lock.
        user["failed_attempts"] += 1
        return {
            "status": "failure",
            "message": "Invalid credentials.",
        }


def authenticate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Module-level helper used by the test suite."""

    service = AuthService()
    return service.authenticate(payload)
