
from context_aware_suggestion_rag.cache.memory import InMemoryCache
from context_aware_suggestion_rag.cache.models import CacheEntry
from context_aware_suggestion_rag.cache.strategies import (
    LRUCacheStrategy,
    TimeBasedCacheStrategy,
    WriteThroughCacheStrategy,
)


# Time-based strategy.
time_strategy = TimeBasedCacheStrategy(ttl_seconds=60)

entry = CacheEntry(
    key="test",
    value="value",
)

assert time_strategy.should_evict("test", entry) is False
print("Time-based cache strategy: PASS")


# LRU strategy.
lru = LRUCacheStrategy(max_entries=2)

lru.record_access("first")
lru.record_access("second")

assert lru.get_eviction_candidate() == "first"

lru.record_access("third")

assert lru.get_eviction_candidate() == "first"

lru.remove("first")

assert lru.get_eviction_candidate() == "second"

print("LRU cache strategy: PASS")


# Write-through strategy.
class FakeStorage:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value


storage = FakeStorage()
cache = InMemoryCache()

write_through = WriteThroughCacheStrategy(storage)

write_through.write("document:1", "hello", cache)

assert storage.get("document:1") == "hello"
assert cache.get("document:1") == "hello"

print("Write-through cache strategy: PASS")


# Read-through fallback.
cache.delete("document:1")

value = write_through.read("document:1", cache)

assert value == "hello"
assert cache.get("document:1") == "hello"

print("Write-through read fallback: PASS")

cache.close()

print("All cache strategy tests passed.")
