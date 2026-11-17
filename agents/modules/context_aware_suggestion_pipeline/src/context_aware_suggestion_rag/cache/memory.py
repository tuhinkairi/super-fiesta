"""
In-memory cache provider.

Provides thread-safe cache operations with TTL expiration
and cache performance statistics.
"""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.models import (
    CacheEntry,
    CacheStatistics,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.interfaces.cache_provider import (
    CacheProvider,
)


class InMemoryCache(CacheProvider):
    """Thread-safe in-memory cache implementation."""

    def __init__(
        self,
        *,
        default_ttl: float | None = None,
        max_entries: int = 10000,
    ) -> None:
        if default_ttl is not None:
            if (
                isinstance(default_ttl, bool)
                or not isinstance(default_ttl, (int, float))
                or default_ttl <= 0
            ):
                raise ValueError(
                    "default_ttl must be a positive number or None."
                )

        if (
            isinstance(max_entries, bool)
            or not isinstance(max_entries, int)
            or max_entries <= 0
        ):
            raise ValueError("max_entries must be a positive integer.")

        self.default_ttl = default_ttl
        self.max_entries = max_entries

        self._entries: dict[str, CacheEntry] = {}
        self._statistics = CacheStatistics()
        self._lock = RLock()
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Cache provider is closed.")

    def _validate_key(self, key: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Cache key must be a non-empty string.")

    def _remove_expired(self) -> None:
        expired_keys = [
            key
            for key, entry in self._entries.items()
            if entry.is_expired
        ]

        for key in expired_keys:
            del self._entries[key]
            self._statistics.evictions += 1

    def _make_entry(
        self,
        key: str,
        value: Any,
        ttl: float | None,
    ) -> CacheEntry:
        from datetime import timedelta

        from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.models import (
            current_utc_time,
        )

        now = current_utc_time()

        if ttl is None:
            ttl = self.default_ttl

        expires_at = (
            now + timedelta(seconds=ttl)
            if ttl is not None
            else None
        )

        return CacheEntry(
            key=key,
            value=deepcopy(value),
            created_at=now,
            expires_at=expires_at,
        )

    def get(self, key: str) -> Any | None:
        """Retrieve a cache value."""
        with self._lock:
            self._ensure_open()
            self._validate_key(key)
            self._remove_expired()

            entry = self._entries.get(key)

            if entry is None:
                self._statistics.misses += 1
                return None

            self._statistics.hits += 1
            return deepcopy(entry.value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """Store a value in the cache."""
        with self._lock:
            self._ensure_open()
            self._validate_key(key)

            if ttl is not None:
                if (
                    isinstance(ttl, bool)
                    or not isinstance(ttl, (int, float))
                    or ttl <= 0
                ):
                    raise ValueError("ttl must be a positive number.")

            self._remove_expired()

            if key not in self._entries:
                if len(self._entries) >= self.max_entries:
                    oldest_key = min(
                        self._entries,
                        key=lambda item: self._entries[item].created_at,
                    )
                    del self._entries[oldest_key]
                    self._statistics.evictions += 1

            self._entries[key] = self._make_entry(key, value, ttl)
            self._statistics.sets += 1

    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        with self._lock:
            self._ensure_open()
            self._validate_key(key)

            self._remove_expired()

            if key not in self._entries:
                return False

            del self._entries[key]
            self._statistics.deletes += 1
            return True

    def exists(self, key: str) -> bool:
        """Check whether a valid cache entry exists."""
        with self._lock:
            self._ensure_open()
            self._validate_key(key)
            self._remove_expired()

            return key in self._entries

    def clear(self) -> None:
        """Remove all cache entries."""
        with self._lock:
            self._ensure_open()
            self._entries.clear()

    def health_check(self) -> bool:
        """Check whether the cache provider is operational."""
        with self._lock:
            return not self._closed

    def get_statistics(self) -> CacheStatistics:
        """Return a snapshot of cache statistics."""
        with self._lock:
            return deepcopy(self._statistics)

    def get_entry_count(self) -> int:
        """Return the number of currently valid cache entries."""
        with self._lock:
            self._ensure_open()
            self._remove_expired()
            return len(self._entries)

    def close(self) -> None:
        """Release cache resources."""
        with self._lock:
            self._entries.clear()
            self._closed = True
