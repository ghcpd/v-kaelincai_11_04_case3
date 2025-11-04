"""Corrected authentication service with hardened validation and lockout handling."""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict


class AuthService:
    """Secure authentication workflow used by the fixed test suite."""

    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_SECONDS = 300

    def __init__(self) -> None:
        self._bootstrap_users()

    def _bootstrap_users(self) -> None:
        self.users: Dict[str, Dict[str, Any]] = {
            "alice": {
                "password_hash": self._hash_password("SecurePass123"),
                "failed_attempts": 0,
                "locked_until": None,
                "last_login": None,
            },
            "bob": {
                "password_hash": self._hash_password("Tr1cky!Pass"),
                "failed_attempts": 0,
                "locked_until": None,
                "last_login": None,
            },
        }

    def reset_state(self) -> None:
        self._bootstrap_users()

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        username = payload.get("username")
        password = payload.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return {"error": "Username and password must be strings."}

        username = username.strip()
        if not username or not password:
            return {"error": "Username and password are required."}

        return {"username": username, "password": password}

    def authenticate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {
                "status": "failure",
                "message": "Invalid request payload.",
            }

        validation = self._validate_payload(payload)
        if "error" in validation:
            return {
                "status": "failure",
                "message": validation["error"],
            }

        username = validation["username"]
        password = validation["password"]

        user = self.users.get(username)
        if not user:
            return {
                "status": "failure",
                "message": "Invalid credentials.",
            }

        locked_until = user.get("locked_until")
        now = time.time()
        if locked_until and locked_until > now:
            return {
                "status": "failure",
                "message": "Account locked due to too many failed attempts.",
            }

        incoming_hash = self._hash_password(password)
        if hmac.compare_digest(incoming_hash, user["password_hash"]):
            user["failed_attempts"] = 0
            user["locked_until"] = None
            user["last_login"] = now
            return {
                "status": "success",
                "message": "Login successful.",
            }

        user["failed_attempts"] += 1
        if user["failed_attempts"] >= self.MAX_FAILED_ATTEMPTS:
            user["locked_until"] = now + self.LOCKOUT_SECONDS
            return {
                "status": "failure",
                "message": "Account locked due to too many failed attempts.",
            }

        return {
            "status": "failure",
            "message": "Invalid credentials.",
        }


def authenticate(payload: Dict[str, Any]) -> Dict[str, Any]:
    service = AuthService()
    return service.authenticate(payload)
