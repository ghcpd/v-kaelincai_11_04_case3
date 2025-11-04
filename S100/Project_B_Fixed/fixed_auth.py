"""Corrected authentication module ensuring strict password validation.

The fixed implementation addresses the normalization bug found in the
corresponding buggy version. Passwords are now treated as case-sensitive byte
sequences and are never trimmed or normalized implicitly. Additional safeguards
include structured payload validation, rate-limit tracking, and resilient output
metadata for downstream analytics.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass
class UserRecord:
    username: str
    salt: str
    password_hash: str
    is_locked: bool = False
    max_attempts: int = 3
    attempt_count: int = 0
    lock_expires_at: Optional[float] = None
    cooldown_seconds: float = 30.0
    audit_trail: Optional[Iterable[str]] = None


class AuthenticationError(ValueError):
    """Raised when the payload is malformed or violates validation rules."""


def _hash_password(raw_password: str, salt: str, *, iterations: int = 120_000) -> str:
    """Return a PBKDF2-HMAC-SHA256 hash for robust password storage."""
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return dk.hex()


def _ensure_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise AuthenticationError(f"{field_name} must be a string")
    trimmed = value.strip()
    if trimmed == "":
        raise AuthenticationError(f"{field_name} cannot be empty")
    return value


def _sanitize_username(value: str) -> str:
    """Usernames remain case-insensitive but leading/trailing spaces are removed."""
    return value.strip().lower()


def _serialize(record: UserRecord) -> Dict[str, object]:
    return {
        "username": record.username,
        "is_locked": record.is_locked,
        "attempt_count": record.attempt_count,
        "max_attempts": record.max_attempts,
        "lock_expires_at": record.lock_expires_at,
    }


def _success(record: UserRecord) -> Dict[str, object]:
    return {
        "status": "success",
        "message": "Login successful",
        "user": _serialize(record),
        "attempts_remaining": record.max_attempts,
        "timestamp": time.time(),
    }


def _failure(message: str, record: Optional[UserRecord], attempts_remaining: int, *, locked: bool) -> Dict[str, object]:
    payload = {
        "status": "failure",
        "message": message,
        "attempts_remaining": attempts_remaining,
        "timestamp": time.time(),
        "locked": locked,
    }
    if record is not None:
        payload["user"] = _serialize(record)
    return payload


def authenticate(payload: Dict[str, object], user_store: Optional[Dict[str, UserRecord]] = None) -> Dict[str, object]:
    if not isinstance(payload, dict):
        raise AuthenticationError("payload must be a dictionary")

    if user_store is None:
        user_store = get_default_store()

    raw_username = _ensure_str(payload.get("username"), "username")
    raw_password = _ensure_str(payload.get("password"), "password")

    username = _sanitize_username(raw_username)
    record = user_store.get(username)
    if record is None:
        return _failure("Unknown user", None, 0, locked=False)

    now = time.time()
    if record.lock_expires_at and now < record.lock_expires_at:
        return _failure("Account temporarily locked", record, 0, locked=True)

    if record.is_locked and record.lock_expires_at is None:
        return _failure("Account locked", record, 0, locked=True)

    if record.attempt_count >= record.max_attempts:
        record.is_locked = True
        record.lock_expires_at = now + record.cooldown_seconds
        return _failure("Account locked after repeated failures", record, 0, locked=True)

    candidate_hash = _hash_password(raw_password, record.salt)
    if hmac.compare_digest(candidate_hash, record.password_hash):
        record.attempt_count = 0
        record.is_locked = False
        record.lock_expires_at = None
        return _success(record)

    record.attempt_count += 1
    attempts_remaining = max(record.max_attempts - record.attempt_count, 0)
    if record.attempt_count >= record.max_attempts:
        record.is_locked = True
        record.lock_expires_at = now + record.cooldown_seconds
        return _failure("Account locked after repeated failures", record, 0, locked=True)

    return _failure("Invalid username or password", record, attempts_remaining, locked=False)


def get_default_store() -> Dict[str, UserRecord]:
    return {username: copy.deepcopy(record) for username, record in _BASE_USER_DATA.items()}


def format_result(result: Dict[str, object]) -> Dict[str, object]:
    sanitized = dict(result)
    sanitized.pop("timestamp", None)
    if "user" in sanitized:
        user_info = dict(sanitized["user"])
        user_info.pop("lock_expires_at", None)
        sanitized["user"] = user_info
    return sanitized


_BASE_USER_DATA: Dict[str, UserRecord] = {
    "alice": UserRecord(
        username="alice",
        salt="alice-SALT",
        password_hash=_hash_password("SecurePass123!", "alice-SALT"),
        max_attempts=3,
        cooldown_seconds=15.0,
    ),
    "bob": UserRecord(
        username="bob",
        salt="bob-SALT",
        password_hash=_hash_password("WinterMute2024", "bob-SALT"),
        max_attempts=4,
        cooldown_seconds=15.0,
    ),
    "charlie": UserRecord(
        username="charlie",
        salt="charlie-SALT",
        password_hash=_hash_password("Pa$$wordComplex#1", "charlie-SALT"),
        max_attempts=2,
        cooldown_seconds=20.0,
    ),
}


__all__ = [
    "AuthenticationError",
    "UserRecord",
    "authenticate",
    "get_default_store",
    "format_result",
]
