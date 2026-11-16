"""
Cache package.

Provides cache models, providers, managers, strategies,
services, and factory functions.
"""

from context_aware_suggestion_rag.cache.factory import (
    create_cache_manager,
    create_cache_provider,
    create_cache_service,
)

from context_aware_suggestion_rag.cache.manager import (
    CacheManager,
)

from context_aware_suggestion_rag.cache.memory import (
    InMemoryCache,
)

from context_aware_suggestion_rag.cache.models import (
    CacheEntry,
    CacheOperationResult,
    CacheStatistics,
    current_utc_time,
)

from context_aware_suggestion_rag.cache.service import (
    CacheService,
)

from context_aware_suggestion_rag.cache.strategies import (
    CacheStrategy,
    LRUCacheStrategy,
    StorageBackend,
    TimeBasedCacheStrategy,
    WriteThroughCacheStrategy,
)


__all__ = [
    "CacheEntry",
    "CacheManager",
    "CacheOperationResult",
    "CacheService",
    "CacheStatistics",
    "CacheStrategy",
    "InMemoryCache",
    "LRUCacheStrategy",
    "StorageBackend",
    "TimeBasedCacheStrategy",
    "WriteThroughCacheStrategy",
    "create_cache_manager",
    "create_cache_provider",
    "create_cache_service",
    "current_utc_time",
]
