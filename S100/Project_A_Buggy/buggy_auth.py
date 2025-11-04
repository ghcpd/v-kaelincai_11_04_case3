"""Buggy authentication module used for functional bug analysis.

This implementation intentionally includes a logic flaw in how passwords are
normalized. The authentication routine lowercases and strips passwords before
hashing, which causes distinct passwords that only differ in case or surrounding
whitespace to be treated as identical. As a result, credentials such as
"SecurePass123!" and "securepass123! " are considered equivalent, violating the
expected strict matching behavior. The accompanying test suite demonstrates the
resulting security regression.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class UserRecord:
    username: str
    salt: str
    password_hash: str
    is_locked: bool = False
    max_attempts: int = 3
    attempt_count: int = 0
    last_attempt_ts: Optional[float] = None


def _hash_password(raw_password: str, salt: str) -> str:
    """Return a salted SHA-256 hash of the provided password."""
    digest = hashlib.sha256()
    digest.update(salt.encode("utf-8"))
    digest.update(raw_password.encode("utf-8"))
    return digest.hexdigest()


def _normalize_username(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_password(value: object) -> str:
    """Normalize passwords prior to hashing.

    BUG: The password is coerced to lowercase and stripped, which reduces the
    entropy of the original password and allows visually similar inputs to
    authenticate successfully. The fixed implementation must avoid this bug by
    preserving the original string exactly as provided by the caller and
    validating its type.
    """

    if value is None:
        return ""
    # The logic error lives here: coercing to lowercase collapses distinct
    # passwords that should not match.
    return str(value).strip().lower()


def _serialize(record: UserRecord) -> Dict[str, object]:
    return {
        "username": record.username,
        "is_locked": record.is_locked,
        "attempt_count": record.attempt_count,
        "max_attempts": record.max_attempts,
        "last_attempt_ts": record.last_attempt_ts,
    }


def _success(record: UserRecord, attempts_remaining: int) -> Dict[str, object]:
    return {
        "status": "success",
        "message": "Login successful",
        "user": _serialize(record),
        "attempts_remaining": attempts_remaining,
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
    """Authenticate a user based on the provided payload.

    The payload is expected to contain "username" and "password" keys. Optional
    metadata values are safely ignored. Results contain a status indicator,
    message, and bookkeeping details useful for auditing or rate limiting.
    """

    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    if user_store is None:
        user_store = get_default_store()

    username = _normalize_username(payload.get("username"))
    record = user_store.get(username)
    if record is None:
        return _failure("Unknown user", None, 0, locked=False)

    # Simple guard against SQL injection-like payloads
    password_field = payload.get("password")
    if isinstance(password_field, str) and any(token in password_field for token in ("' OR", "--", "/*")):
        record.attempt_count += 1
        attempts_remaining = max(record.max_attempts - record.attempt_count, 0)
        if record.attempt_count >= record.max_attempts:
            record.is_locked = True
            return _failure("Account locked due to suspicious activity", record, 0, locked=True)
        return _failure("Invalid username or password", record, attempts_remaining, locked=False)

    if record.is_locked or record.attempt_count >= record.max_attempts:
        record.is_locked = True
        return _failure("Account locked", record, 0, locked=True)

    provided_password = _normalize_password(password_field)
    candidate = _hash_password(provided_password, record.salt)
    matches = hmac.compare_digest(candidate, record.password_hash)

    if matches:
        record.attempt_count = 0
        record.last_attempt_ts = time.time()
        return _success(record, record.max_attempts)

    record.attempt_count += 1
    record.last_attempt_ts = time.time()
    attempts_remaining = max(record.max_attempts - record.attempt_count, 0)
    if record.attempt_count >= record.max_attempts:
        record.is_locked = True
        return _failure("Account locked after repeated failures", record, 0, locked=True)
    return _failure("Invalid username or password", record, attempts_remaining, locked=False)


def get_default_store() -> Dict[str, UserRecord]:
    """Return a fresh, mutable copy of the default in-memory user store."""
    return {username: copy.deepcopy(record) for username, record in _BASE_USER_DATA.items()}


def format_result(result: Dict[str, object]) -> Dict[str, object]:
    """Drop volatile fields to simplify deterministic comparisons in tests."""
    sanitized = dict(result)
    sanitized.pop("timestamp", None)
    if "user" in sanitized:
        user_info = dict(sanitized["user"])
        user_info.pop("last_attempt_ts", None)
        sanitized["user"] = user_info
    return sanitized


# Construct the baseline store with intentionally weak password handling.
_BASE_USER_DATA: Dict[str, UserRecord] = {
    "alice": UserRecord(
        username="alice",
        salt="alice-SALT",
        # Intentional misuse: password stored using normalized (lowercased) value
        password_hash=_hash_password("securepass123!", "alice-SALT"),
        max_attempts=3,
    ),
    "bob": UserRecord(
        username="bob",
        salt="bob-SALT",
        password_hash=_hash_password("wintermute2024", "bob-SALT"),
        max_attempts=4,
    ),
    "charlie": UserRecord(
        username="charlie",
        salt="charlie-SALT",
        password_hash=_hash_password("Pa$$wordComplex#1", "charlie-SALT"),
        max_attempts=2,
    ),
}


__all__ = [
    "UserRecord",
    "authenticate",
    "get_default_store",
    "format_result",
]
