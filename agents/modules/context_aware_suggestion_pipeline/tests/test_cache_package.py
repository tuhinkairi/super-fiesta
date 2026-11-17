
from context_aware_suggestion_rag.cache import (
    CacheEntry,
    CacheManager,
    CacheOperationResult,
    CacheService,
    CacheStatistics,
    CacheStrategy,
    InMemoryCache,
    LRUCacheStrategy,
    StorageBackend,
    TimeBasedCacheStrategy,
    WriteThroughCacheStrategy,
    create_cache_manager,
    create_cache_provider,
    create_cache_service,
    current_utc_time,
)


exports = [
    CacheEntry,
    CacheManager,
    CacheOperationResult,
    CacheService,
    CacheStatistics,
    CacheStrategy,
    InMemoryCache,
    LRUCacheStrategy,
    StorageBackend,
    TimeBasedCacheStrategy,
    WriteThroughCacheStrategy,
    create_cache_manager,
    create_cache_provider,
    create_cache_service,
    current_utc_time,
]

assert len(exports) == 15
assert len(set(exports)) == 15

print("Cache package imports: PASS")
print("Cache package export count: PASS")
print("All cache package exports passed.")
