
from context_aware_suggestion_rag.interfaces.cache_provider import (
    CacheProvider,
)


class FakeCacheProvider(CacheProvider):

    def __init__(self):
        self.storage = {}

    def get(self, key):
        return self.storage.get(key)

    def set(self, key, value, ttl=None):
        self.storage[key] = value

    def delete(self, key):
        return self.storage.pop(key, None) is not None

    def exists(self, key):
        return key in self.storage

    def clear(self):
        self.storage.clear()

    def health_check(self):
        return True


def main():
    cache = FakeCacheProvider()

    assert isinstance(cache, CacheProvider)
    print("Cache provider inheritance: PASS")

    assert cache.health_check()
    print("Cache health check: PASS")

    cache.set("user_1", {"name": "Test"}, ttl=60)

    assert cache.get("user_1") == {"name": "Test"}
    print("Cache set and get: PASS")

    assert cache.exists("user_1")
    assert not cache.exists("missing")
    print("Cache existence check: PASS")

    assert cache.delete("user_1")
    assert cache.get("user_1") is None
    print("Cache deletion: PASS")

    cache.set("key_1", "value_1")
    cache.set("key_2", "value_2")
    cache.clear()

    assert not cache.exists("key_1")
    assert not cache.exists("key_2")
    print("Cache clearing: PASS")

    cache.close()
    print("Cache close interface: PASS")

    print("\nAll cache provider interface tests passed.")


if __name__ == "__main__":
    main()
