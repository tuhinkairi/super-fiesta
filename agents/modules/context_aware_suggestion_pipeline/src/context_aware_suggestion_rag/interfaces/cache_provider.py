"""
Cache provider interfaces.

Defines a common contract for interchangeable caching backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    """Abstract contract for cache implementations."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a cached value."""
        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Store a value with an optional time-to-live."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check whether a cache key exists."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all cached values."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the cache backend is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release backend resources when applicable."""
        return None
