"""
Cache strategies.

Provides reusable strategies for cache expiration, eviction,
and write-through behavior.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Any, Protocol


class CacheStrategy(ABC):
    """Base interface for cache strategies."""

    @abstractmethod
    def should_evict(self, key: str, value: Any) -> bool:
        """Determine whether a cache entry should be evicted."""
        raise NotImplementedError


@dataclass(slots=True)
class TimeBasedCacheStrategy(CacheStrategy):
    """Defines a default TTL for cache entries."""

    ttl_seconds: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.ttl_seconds, bool)
            or not isinstance(self.ttl_seconds, (int, float))
            or self.ttl_seconds <= 0
        ):
            raise ValueError("ttl_seconds must be positive.")

    def should_evict(self, key: str, value: Any) -> bool:
        return bool(getattr(value, "is_expired", False))


class LRUCacheStrategy(CacheStrategy):
    """Tracks recently accessed keys for least-recently-used eviction."""

    def __init__(self, max_entries: int = 1000) -> None:
        if (
            isinstance(max_entries, bool)
            or not isinstance(max_entries, int)
            or max_entries <= 0
        ):
            raise ValueError("max_entries must be positive.")

        self.max_entries = max_entries
        self._access_order: OrderedDict[str, None] = OrderedDict()
        self._lock = RLock()

    def record_access(self, key: str) -> None:
        """Mark a key as recently accessed."""
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string.")

        with self._lock:
            self._access_order.pop(key, None)
            self._access_order[key] = None

    def remove(self, key: str) -> None:
        """Remove a key from the access tracker."""
        with self._lock:
            self._access_order.pop(key, None)

    def get_eviction_candidate(self) -> str | None:
        """Return the least recently used key."""
        with self._lock:
            if len(self._access_order) < self.max_entries:
                return None

            return next(iter(self._access_order), None)

    def should_evict(self, key: str, value: Any) -> bool:
        """Determine whether the tracked key exceeds capacity."""
        with self._lock:
            return (
                key in self._access_order
                and len(self._access_order) > self.max_entries
            )


class StorageBackend(Protocol):
    """Minimal contract for write-through storage backends."""

    def get(self, key: str) -> Any | None:
        ...

    def set(self, key: str, value: Any) -> None:
        ...


class WriteThroughCacheStrategy(CacheStrategy):
    """Writes values to both cache and persistent storage."""

    def __init__(self, storage: StorageBackend) -> None:
        if not callable(getattr(storage, "get", None)):
            raise TypeError("storage must implement get().")

        if not callable(getattr(storage, "set", None)):
            raise TypeError("storage must implement set().")

        self.storage = storage

    def write(self, key: str, value: Any, cache: Any) -> None:
        """Write a value to persistent storage and cache."""
        self.storage.set(key, value)
        cache.set(key, value)

    def read(self, key: str, cache: Any) -> Any | None:
        """Read from cache, falling back to persistent storage."""
        value = cache.get(key)

        if value is not None:
            return value

        value = self.storage.get(key)

        if value is not None:
            cache.set(key, value)

        return value

    def should_evict(self, key: str, value: Any) -> bool:
        """Write-through entries are not evicted by this strategy."""
        return False
