"""
Cache package.

Provides cache models, providers, managers, strategies,
services, and factory functions.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.factory import (
    create_cache_manager,
    create_cache_provider,
    create_cache_service,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.manager import (
    CacheManager,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.memory import (
    InMemoryCache,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.models import (
    CacheEntry,
    CacheOperationResult,
    CacheStatistics,
    current_utc_time,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.service import (
    CacheService,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.cache.strategies import (
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
