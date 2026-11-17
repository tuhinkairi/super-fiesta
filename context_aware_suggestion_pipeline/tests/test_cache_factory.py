from context_aware_suggestion_rag.cache.factory import (
    create_cache_manager,
    create_cache_provider,
    create_cache_service,
)
from context_aware_suggestion_rag.cache.memory import InMemoryCache


# Provider factory.
provider = create_cache_provider("memory")

assert isinstance(provider, InMemoryCache)

print("Cache provider factory: PASS")


# Manager factory.
manager = create_cache_manager(
    namespace="factory-test",
)

manager.set("item", "value")

assert manager.get("item") == "value"

print("Cache manager factory: PASS")


# Service factory.
service = create_cache_service(
    namespace="factory-service",
    enable_lru=True,
    lru_max_entries=5,
)

service.set("item", "value")

assert service.get("item") == "value"
assert service.health_check() is True

print("Cache service factory: PASS")


# Invalid provider.
try:
    create_cache_provider("unsupported")
    raise AssertionError("Unsupported provider was accepted.")
except ValueError:
    pass

print("Cache provider validation: PASS")


provider.close()
manager.close()
service.close()

print("All cache factory tests passed.")
