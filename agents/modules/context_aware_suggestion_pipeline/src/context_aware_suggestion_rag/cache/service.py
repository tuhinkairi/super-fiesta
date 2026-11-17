"""
Cache service.

Provides a unified service for application-level caching.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.manager import CacheManager
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.models import CacheStatistics
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.strategies import (
    LRUCacheStrategy,
)


class CacheService:
    """High-level cache service for application components."""

    def __init__(
        self,
        manager: CacheManager | None = None,
        *,
        lru_strategy: LRUCacheStrategy | None = None,
    ) -> None:
        self.manager = manager or CacheManager()
        self.lru_strategy = lru_strategy
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Cache service is closed.")

    def get(self, key: str) -> Any | None:
        """Retrieve a value and update its LRU access record."""
        self._ensure_open()

        value = self.manager.get(key)

        if value is not None and self.lru_strategy is not None:
            self.lru_strategy.record_access(key)

        return value

    def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """Store a value in the cache."""
        self._ensure_open()

        self.manager.set(key, value, ttl=ttl)

        if self.lru_strategy is not None:
            self.lru_strategy.record_access(key)

    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        self._ensure_open()

        deleted = self.manager.delete(key)

        if deleted and self.lru_strategy is not None:
            self.lru_strategy.remove(key)

        return deleted

    def exists(self, key: str) -> bool:
        """Check whether a cache entry exists."""
        self._ensure_open()
        return self.manager.exists(key)

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: float | None = None,
    ) -> Any:
        """Retrieve a cached value or compute and store it."""
        self._ensure_open()

        value = self.manager.get_or_set(
            key,
            factory,
            ttl=ttl,
        )

        if self.lru_strategy is not None:
            self.lru_strategy.record_access(key)

        return value

    def get_statistics(self) -> CacheStatistics | None:
        """Return statistics when supported by the provider."""
        self._ensure_open()

        provider = self.manager.provider
        get_statistics = getattr(provider, "get_statistics", None)

        if not callable(get_statistics):
            return None

        return get_statistics()

    def get_entry_count(self) -> int | None:
        """Return entry count when supported by the provider."""
        self._ensure_open()

        provider = self.manager.provider
        get_entry_count = getattr(provider, "get_entry_count", None)

        if not callable(get_entry_count):
            return None

        return get_entry_count()

    def health_check(self) -> bool:
        """Check cache service health."""
        if self._closed:
            return False

        return self.manager.health_check()

    def clear(self) -> None:
        """Clear the underlying cache."""
        self._ensure_open()
        self.manager.clear()

    def close(self) -> None:
        """Close the cache service."""
        if not self._closed:
            self.manager.close()
            self._closed = True
