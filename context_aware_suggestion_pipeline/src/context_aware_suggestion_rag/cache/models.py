"""
Cache data models.

Defines structured representations for cache entries,
statistics, and cache operation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class CacheEntry:
    """Represents a stored cache entry."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=current_utc_time)
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("Cache key must be a non-empty string.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware.")

        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime):
                raise TypeError("expires_at must be a datetime.")

            if self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware.")

            if self.expires_at <= self.created_at:
                raise ValueError("expires_at must be after created_at.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @property
    def is_expired(self) -> bool:
        """Return whether this entry has expired."""
        if self.expires_at is None:
            return False

        return current_utc_time() >= self.expires_at

    @property
    def ttl_seconds(self) -> float | None:
        """Return remaining lifetime in seconds."""
        if self.expires_at is None:
            return None

        remaining = (
            self.expires_at - current_utc_time()
        ).total_seconds()

        return max(0.0, remaining)


@dataclass(slots=True)
class CacheStatistics:
    """Tracks cache performance statistics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    errors: int = 0

    def __post_init__(self) -> None:
        for name in (
            "hits",
            "misses",
            "sets",
            "deletes",
            "evictions",
            "errors",
        ):
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

    @property
    def total_requests(self) -> int:
        """Return the total number of cache reads."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Return cache hit rate between 0 and 1."""
        total = self.total_requests

        if total == 0:
            return 0.0

        return self.hits / total

    @property
    def miss_rate(self) -> float:
        """Return cache miss rate between 0 and 1."""
        total = self.total_requests

        if total == 0:
            return 0.0

        return self.misses / total


@dataclass(slots=True)
class CacheOperationResult:
    """Represents the outcome of a cache operation."""

    success: bool
    operation: str
    key: str | None = None
    message: str = ""
    timestamp: datetime = field(default_factory=current_utc_time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean.")

        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.key is not None:
            if not isinstance(self.key, str) or not self.key.strip():
                raise ValueError("key must be a non-empty string.")

        if not isinstance(self.message, str):
            raise TypeError("message must be a string.")

        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime.")

        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")
