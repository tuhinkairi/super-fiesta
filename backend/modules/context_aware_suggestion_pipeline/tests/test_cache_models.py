
from datetime import timedelta

from context_aware_suggestion_rag.cache.models import (
    CacheEntry,
    CacheOperationResult,
    CacheStatistics,
    current_utc_time,
)


# Cache entry.
entry = CacheEntry(
    key="document:123",
    value={"content": "Hello world"},
)

assert entry.key == "document:123"
assert entry.is_expired is False
assert entry.ttl_seconds is None

print("Cache entry creation: PASS")


# Expiring cache entry.
now = current_utc_time()

expiring_entry = CacheEntry(
    key="temporary:item",
    value="temporary",
    created_at=now - timedelta(minutes=2),
    expires_at=now - timedelta(minutes=1),
)

assert expiring_entry.is_expired is True
assert expiring_entry.ttl_seconds == 0.0

print("Cache expiration: PASS")


# Cache statistics.
statistics = CacheStatistics(
    hits=80,
    misses=20,
    sets=30,
    deletes=5,
)

assert statistics.total_requests == 100
assert statistics.hit_rate == 0.8
assert statistics.miss_rate == 0.2

print("Cache statistics: PASS")


# Cache operation result.
result = CacheOperationResult(
    success=True,
    operation="set",
    key="document:123",
    message="Cache entry stored.",
)

assert result.success is True
assert result.operation == "set"

print("Cache operation result: PASS")


# Validation.
try:
    CacheEntry(key="", value="invalid")
    raise AssertionError("Invalid cache key was accepted.")
except ValueError:
    pass

print("Cache model validation: PASS")
print("All cache model tests passed.")
