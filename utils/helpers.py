"""
utils/helpers.py — Miscellaneous test-support utilities.
"""

from __future__ import annotations

import random
import string
import time
from datetime import datetime
from typing import Any


# ── Random data generators ────────────────────────────────────────────────────

def random_string(length: int = 8, prefix: str = "") -> str:
    chars = string.ascii_lowercase + string.digits
    return prefix + "".join(random.choices(chars, k=length))


def random_email(domain: str = "test.example.com") -> str:
    return f"{random_string(8)}@{domain}"


def random_phone(country_code: str = "+1") -> str:
    digits = "".join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{country_code}{digits}"


def timestamp_string(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now().strftime(fmt)


# ── Retry helper ──────────────────────────────────────────────────────────────

def retry(
    func,
    *,
    retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Any:
    """
    Call *func* up to *retries* times, sleeping *delay* seconds between attempts.

    Usage:
        result = retry(lambda: api.get("/unstable"), retries=5, delay=2)
    """
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]


# ── Date/time helpers ─────────────────────────────────────────────────────────

def iso_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def future_date(days: int = 30, fmt: str = "%Y-%m-%d") -> str:
    from datetime import timedelta
    return (datetime.utcnow() + timedelta(days=days)).strftime(fmt)


# ── Assertion utilities ───────────────────────────────────────────────────────

def assert_subset(subset: dict, superset: dict) -> None:
    """Assert every key/value in *subset* appears in *superset*."""
    for key, value in subset.items():
        assert key in superset, f"Key '{key}' missing from response."
        assert superset[key] == value, (
            f"Key '{key}': expected {value!r}, got {superset[key]!r}"
        )


def assert_list_not_empty(items: list, label: str = "list") -> None:
    assert len(items) > 0, f"Expected {label} to be non-empty."
