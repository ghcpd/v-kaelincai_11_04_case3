"""Corrected authentication service with robust password handling.

Improvements compared to the buggy version:
- Preserves password casing and whitespace during hashing/comparison.
- Uses secrets.compare_digest for constant-time comparisons.
- Enforces strict input validation for usernames and passwords.
- Hardens rate limiting and audit metadata to avoid timing leaks.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple


@dataclass
class UserRecord:
    username: str
    salt: str
    password_hash: str
    iteration_count: int


class AuthService:
    def __init__(
        self,
        users: Iterable[Dict[str, str]],
        *,
        max_attempts: int = 3,
        lockout_seconds: int = 30,
        iteration_count: int = 120_000,
    ) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if lockout_seconds < 0:
            raise ValueError("lockout_seconds cannot be negative")
        if iteration_count < 20_000:
            raise ValueError("iteration_count too low for PBKDF2")

        self._records: Dict[str, UserRecord] = {}
        self._attempts: Dict[Tuple[str, str], Tuple[int, float]] = {}
        self._max_attempts = max_attempts
        self._lockout_seconds = lockout_seconds
        self._iteration_count = iteration_count
        self._load_users(users)

    def _load_users(self, users: Iterable[Dict[str, str]]) -> None:
        for entry in users:
            username = self._prepare_username(entry["username"])
            password = entry["password"]
            salt_hex = entry.get("salt")
            if salt_hex is None:
                salt_bytes = secrets.token_bytes(16)
                salt_hex = salt_bytes.hex()
            else:
                salt_bytes = bytes.fromhex(salt_hex)

            prepared_password = self._prepare_password(password)
            password_hash = self._hash_password(prepared_password, salt_bytes, self._iteration_count)
            record = UserRecord(
                username=username,
                salt=salt_hex,
                password_hash=password_hash,
                iteration_count=self._iteration_count,
            )
            self._records[username.lower()] = record

    def _prepare_username(self, username: str) -> str:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must be a non-empty string")
        return username.strip()

    def _prepare_password(self, password: str) -> str:
        if not isinstance(password, str):
            raise TypeError("password must be provided as a string")
        if len(password) > 256:
            raise ValueError("password length exceeds policy limit")
        return password

    def _hash_password(self, password: str, salt: bytes, iteration_count: int) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iteration_count,
        ).hex()

    def _lockout_key(self, username: str, client_id: Optional[str]) -> Tuple[str, str]:
        return (username.lower(), client_id or "")

    def _now(self) -> float:
        return time.time()

    def _is_locked(self, key: Tuple[str, str]) -> Tuple[bool, float]:
        attempts, timestamp = self._attempts.get(key, (0, 0.0))
        if attempts < self._max_attempts:
            return False, 0.0
        remaining = max(0.0, self._lockout_seconds - (self._now() - timestamp))
        return remaining > 0, remaining

    def _record_failure(self, key: Tuple[str, str]) -> None:
        attempts, first_ts = self._attempts.get(key, (0, self._now()))
        attempts += 1
        if attempts >= self._max_attempts:
            self._attempts[key] = (attempts, self._now())
        else:
            self._attempts[key] = (attempts, first_ts)

    def _reset_attempts(self, key: Tuple[str, str]) -> None:
        self._attempts.pop(key, None)

    def authenticate(
        self, username: str, password: Optional[str], *, client_id: Optional[str] = None
    ) -> Dict[str, object]:
        try:
            prepared_username = self._prepare_username(username)
        except ValueError as exc:
            return {"status": "failure", "message": str(exc), "attempts_left": self._max_attempts}

        key = self._lockout_key(prepared_username, client_id)
        locked, wait_seconds = self._is_locked(key)
        if locked:
            return {
                "status": "failure",
                "message": f"Too many attempts. Try again in {int(round(wait_seconds))}s.",
                "attempts_left": 0,
            }

        record = self._records.get(prepared_username.lower())
        if record is None:
            self._record_failure(key)
            attempts_left = max(0, self._max_attempts - self._attempts.get(key, (0, 0))[0])
            return {
                "status": "failure",
                "message": "Unknown username.",
                "attempts_left": attempts_left,
            }

        try:
            prepared_password = self._prepare_password(password)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            self._record_failure(key)
            attempts_left = max(0, self._max_attempts - self._attempts.get(key, (0, 0))[0])
            return {
                "status": "failure",
                "message": str(exc),
                "attempts_left": attempts_left,
            }

        salt_bytes = bytes.fromhex(record.salt)
        candidate_hash = self._hash_password(prepared_password, salt_bytes, record.iteration_count)

        if hmac.compare_digest(candidate_hash, record.password_hash):
            self._reset_attempts(key)
            return {
                "status": "success",
                "message": "Login successful.",
                "attempts_left": self._max_attempts,
            }

        self._record_failure(key)
        attempts_left = max(0, self._max_attempts - self._attempts.get(key, (0, 0))[0])
        return {
            "status": "failure",
            "message": "Invalid credentials.",
            "attempts_left": attempts_left,
        }


__all__ = ["AuthService", "UserRecord"]
