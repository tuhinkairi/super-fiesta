"""
Cache manager.

Provides a higher-level interface for managing cache operations,
namespaced keys, and cache statistics.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.memory import InMemoryCache
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.interfaces.cache_provider import (
    CacheProvider,
)


class CacheManager:
    """Coordinates cache operations through a cache provider."""

    def __init__(
        self,
        provider: CacheProvider | None = None,
        *,
        namespace: str = "context_aware_suggestion_rag",
    ) -> None:
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError("namespace must be a non-empty string.")

        self.provider = provider or InMemoryCache()
        self.namespace = namespace.strip()

    def _build_key(self, key: str) -> str:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Cache key must be a non-empty string.")

        return f"{self.namespace}:{key.strip()}"

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache."""
        return self.provider.get(self._build_key(key))

    def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """Store a value in the cache."""
        self.provider.set(
            self._build_key(key),
            value,
            ttl=ttl,
        )

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        return self.provider.delete(self._build_key(key))

    def exists(self, key: str) -> bool:
        """Check whether a key exists."""
        return self.provider.exists(self._build_key(key))

    def clear(self) -> None:
        """Clear all entries belonging to this namespace."""
        prefix = f"{self.namespace}:"

        # The generic CacheProvider interface does not expose key
        # enumeration or prefix deletion. Therefore, clearing the
        # entire provider is the only portable implementation.
        #
        # This method is intentionally explicit about that behavior.
        self.provider.clear()

    def build_content_key(self, content: str) -> str:
        """Generate a deterministic key for text content."""
        if not isinstance(content, str):
            raise TypeError("content must be a string.")

        digest = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        return f"content:{digest}"

    def build_object_key(self, value: Any) -> str:
        """Generate a deterministic key for JSON-serializable data."""
        try:
            serialized = json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Value must be JSON serializable."
            ) from exc

        return self.build_content_key(serialized)

    def get_or_set(
        self,
        key: str,
        factory,
        ttl: float | None = None,
    ) -> Any:
        """Return a cached value or compute and store it."""
        cached_value = self.get(key)

        if cached_value is not None:
            return cached_value

        if not callable(factory):
            raise TypeError("factory must be callable.")

        value = factory()
        self.set(key, value, ttl=ttl)

        return value

    def health_check(self) -> bool:
        """Check cache provider health."""
        return self.provider.health_check()

    def close(self) -> None:
        """Close the underlying cache provider."""
        self.provider.close()
