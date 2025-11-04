"""Buggy authentication service demonstrating a functional defect.

This module intentionally contains a logic flaw around password normalization.
It lowercases passwords before hashing them, causing case-insensitive password
checks that allow incorrect credentials to pass if they match ignoring case.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple


@dataclass
class UserRecord:
    username: str
    salt: str
    password_hash: str


class AuthService:
    """Simplified authentication service with intentional bug.

    The service stores salted password hashes for each user and supports basic
    rate limiting. The defect lies in the password normalization logic used
    both during storage and validation: passwords are coerced to lowercase,
    making the comparison case-insensitive.
    """

    def __init__(
        self,
        users: Iterable[Dict[str, str]],
        *,
        max_attempts: int = 3,
        lockout_seconds: int = 30,
    ) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if lockout_seconds < 0:
            raise ValueError("lockout_seconds cannot be negative")

        self._records: Dict[str, UserRecord] = {}
        self._attempts: Dict[Tuple[str, str], Tuple[int, float]] = {}
        self._max_attempts = max_attempts
        self._lockout_seconds = lockout_seconds
        self._load_users(users)

    def _load_users(self, users: Iterable[Dict[str, str]]) -> None:
        for entry in users:
            username = entry["username"].strip()
            password = entry["password"]
            salt = entry.get("salt")
            if salt is None:
                salt_bytes = secrets.token_bytes(16)
                salt = salt_bytes.hex()
            else:
                salt_bytes = bytes.fromhex(salt)

            normalized = self._normalize_password(password)
            password_hash = self._hash_password(normalized, salt_bytes)
            record = UserRecord(username=username, salt=salt, password_hash=password_hash)
            self._records[username.lower()] = record

    def _normalize_password(self, password: str) -> str:
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        # BUG: `.lower()` causes passwords to be treated case-insensitively.
        return password.strip().lower()

    def _hash_password(self, password: str, salt: bytes) -> str:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 60000).hex()

    def _lockout_key(self, username: str, client_id: Optional[str]) -> Tuple[str, str]:
        return (username, client_id or "")

    def _now(self) -> float:
        return time.time()

    def _register_failure(self, key: Tuple[str, str]) -> None:
        attempts, first_failure = self._attempts.get(key, (0, self._now()))
        attempts += 1
        if attempts >= self._max_attempts:
            self._attempts[key] = (attempts, self._now())
        else:
            self._attempts[key] = (attempts, first_failure)

    def _reset_attempts(self, key: Tuple[str, str]) -> None:
        if key in self._attempts:
            del self._attempts[key]

    def _is_locked_out(self, key: Tuple[str, str]) -> bool:
        attempts, last_failure_time = self._attempts.get(key, (0, 0.0))
        if attempts < self._max_attempts:
            return False
        return (self._now() - last_failure_time) < self._lockout_seconds

    def authenticate(
        self, username: str, password: Optional[str], *, client_id: Optional[str] = None
    ) -> Dict[str, str]:
        if not isinstance(username, str) or not username.strip():
            return {
                "status": "failure",
                "message": "Username must be a non-empty string.",
            }

        normalized_username = username.strip().lower()
        record = self._records.get(normalized_username)
        if record is None:
            return {"status": "failure", "message": "Unknown username."}

        key = self._lockout_key(normalized_username, client_id)
        if self._is_locked_out(key):
            remaining = int(round(self._lockout_seconds - (self._now() - self._attempts[key][1])))
            return {
                "status": "failure",
                "message": f"Too many attempts. Try again in {max(0, remaining)}s.",
            }

        try:
            prepared = self._normalize_password(password)  # type: ignore[arg-type]
        except TypeError:
            self._register_failure(key)
            return {"status": "failure", "message": "Password must be a string."}

        salt_bytes = bytes.fromhex(record.salt)
        candidate_hash = self._hash_password(prepared, salt_bytes)
        if candidate_hash == record.password_hash:
            self._reset_attempts(key)
            return {"status": "success", "message": "Login successful."}

        self._register_failure(key)
        attempts_left = max(0, self._max_attempts - self._attempts.get(key, (0, 0))[0])
        return {
            "status": "failure",
            "message": f"Invalid credentials. Attempts left: {attempts_left}.",
        }


__all__ = ["AuthService", "UserRecord"]
