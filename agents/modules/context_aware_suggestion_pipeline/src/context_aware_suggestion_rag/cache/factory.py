"""
Cache factory.

Provides centralized construction of cache providers,
managers, and services.
"""

from __future__ import annotations

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.manager import CacheManager
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.memory import InMemoryCache
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.service import CacheService
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.strategies import (
    LRUCacheStrategy,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.interfaces.cache_provider import (
    CacheProvider,
)


def create_cache_provider(
    provider_name: str = "memory",
    *,
    default_ttl: float | None = None,
    max_entries: int = 10000,
) -> CacheProvider:
    """Create a cache provider by name."""
    if not isinstance(provider_name, str) or not provider_name.strip():
        raise ValueError("provider_name must be a non-empty string.")

    normalized_name = provider_name.strip().lower()

    if normalized_name in {"memory", "in_memory", "local"}:
        return InMemoryCache(
            default_ttl=default_ttl,
            max_entries=max_entries,
        )

    raise ValueError(
        f"Unsupported cache provider: {provider_name}"
    )


def create_cache_manager(
    provider: CacheProvider | None = None,
    *,
    namespace: str = "context_aware_suggestion_rag",
    default_ttl: float | None = None,
    max_entries: int = 10000,
) -> CacheManager:
    """Create a cache manager."""
    if provider is None:
        provider = create_cache_provider(
            default_ttl=default_ttl,
            max_entries=max_entries,
        )

    return CacheManager(
        provider=provider,
        namespace=namespace,
    )


def create_cache_service(
    provider: CacheProvider | None = None,
    *,
    namespace: str = "context_aware_suggestion_rag",
    default_ttl: float | None = None,
    max_entries: int = 10000,
    enable_lru: bool = False,
    lru_max_entries: int = 1000,
) -> CacheService:
    """Create a fully configured cache service."""
    manager = create_cache_manager(
        provider=provider,
        namespace=namespace,
        default_ttl=default_ttl,
        max_entries=max_entries,
    )

    lru_strategy = (
        LRUCacheStrategy(max_entries=lru_max_entries)
        if enable_lru
        else None
    )

    return CacheService(
        manager=manager,
        lru_strategy=lru_strategy,
    )
