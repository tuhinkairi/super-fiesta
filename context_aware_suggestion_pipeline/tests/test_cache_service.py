from context_aware_suggestion_rag.cache.manager import CacheManager
from context_aware_suggestion_rag.cache.memory import InMemoryCache
from context_aware_suggestion_rag.cache.service import CacheService
from context_aware_suggestion_rag.cache.strategies import (
    LRUCacheStrategy,
)


provider = InMemoryCache(max_entries=10)
manager = CacheManager(
    provider,
    namespace="service-test",
)

lru = LRUCacheStrategy(max_entries=3)

service = CacheService(
    manager,
    lru_strategy=lru,
)

# Set and get.
service.set("item:1", "hello")

assert service.get("item:1") == "hello"

print("Cache service set and get: PASS")


# Get or set.
calls = {"count": 0}


def factory():
    calls["count"] += 1
    return "generated"


assert service.get_or_set("generated", factory) == "generated"
assert service.get_or_set("generated", factory) == "generated"
assert calls["count"] == 1

print("Cache service get-or-set: PASS")


# Delete.
assert service.delete("item:1") is True
assert service.exists("item:1") is False

print("Cache service deletion: PASS")


# Statistics.
statistics = service.get_statistics()

assert statistics is not None
assert statistics.sets == 2

print("Cache service statistics: PASS")


# Entry count.
assert service.get_entry_count() == 1

print("Cache service entry count: PASS")


# Health check.
assert service.health_check() is True

service.close()

assert service.health_check() is False

print("Cache service health check and close: PASS")
print("All cache service tests passed.")
