
import time

from context_aware_suggestion_rag.cache.memory import InMemoryCache


cache = InMemoryCache(default_ttl=5)

# Set and retrieve.
cache.set("user:1", {"name": "Rohan"})

assert cache.get("user:1") == {"name": "Rohan"}
print("Cache set and get: PASS")

# Verify defensive copying.
value = cache.get("user:1")
value["name"] = "Modified"

assert cache.get("user:1") == {"name": "Rohan"}
print("Cache defensive copying: PASS")

# Check existence.
assert cache.exists("user:1") is True
assert cache.exists("missing") is False
print("Cache existence check: PASS")

# Delete.
assert cache.delete("user:1") is True
assert cache.delete("user:1") is False
print("Cache deletion: PASS")

# TTL expiration.
cache.set("temporary", "value", ttl=0.1)

assert cache.exists("temporary") is True

time.sleep(0.2)

assert cache.exists("temporary") is False
print("Cache TTL expiration: PASS")


# Statistics.
cache.set("statistics:test", "value")
cache.get("statistics:test")
cache.get("missing")

statistics = cache.get_statistics()

assert statistics.hits == 4
assert statistics.misses == 1
assert statistics.sets == 3

print("Cache statistics: PASS")


# Health check.
assert cache.health_check() is True
cache.close()

assert cache.health_check() is False

print("Cache health check and close: PASS")
print("All in-memory cache tests passed.")
