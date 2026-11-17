
from context_aware_suggestion_rag.cache.manager import CacheManager


manager = CacheManager(namespace="test")

# Basic cache operations.
manager.set("user:1", {"name": "Rohan"})

assert manager.get("user:1") == {"name": "Rohan"}
print("Cache manager set and get: PASS")

# Existence and deletion.
assert manager.exists("user:1") is True
assert manager.delete("user:1") is True
assert manager.exists("user:1") is False

print("Cache manager existence and deletion: PASS")

# Content-based key.
key1 = manager.build_content_key("hello")
key2 = manager.build_content_key("hello")

assert key1 == key2
print("Content-based cache key: PASS")

# Object-based key.
object_key1 = manager.build_object_key({"a": 1, "b": 2})
object_key2 = manager.build_object_key({"b": 2, "a": 1})

assert object_key1 == object_key2
print("Object-based cache key: PASS")

# Get or set.
calls = {"count": 0}


def factory():
    calls["count"] += 1
    return "generated"


assert manager.get_or_set("generated", factory) == "generated"
assert manager.get_or_set("generated", factory) == "generated"
assert calls["count"] == 1

print("Cache get-or-set: PASS")

# Health check.
assert manager.health_check() is True
print("Cache manager health check: PASS")

manager.close()

print("All cache manager tests passed.")
