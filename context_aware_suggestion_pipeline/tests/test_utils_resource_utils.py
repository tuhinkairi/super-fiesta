
from context_aware_suggestion_rag.utils.resource_utils import (
    ResourceCleanupError,
    ResourceRegistry,
    register_resource,
)


class FakeResource:
    def __init__(self, name):
        self.name = name
        self.closed = False

    def close(self):
        self.closed = True


def test_register_resource():
    registry = ResourceRegistry()
    resource = FakeResource("database")

    registration = registry.register(resource)

    assert registration.resource_name == "FakeResource"
    assert registry.resource_count == 1
    assert registry.contains(registration.token)


def test_release_resource():
    registry = ResourceRegistry()
    resource = FakeResource("cache")

    registration = registry.register(resource)

    assert registry.release(registration.token) is True
    assert resource.closed is True
    assert registry.resource_count == 0
    assert registry.release(registration.token) is False


def test_reverse_cleanup_order():
    registry = ResourceRegistry()
    cleanup_order = []

    registry.register(
        object(),
        cleanup=lambda: cleanup_order.append("first"),
    )
    registry.register(
        object(),
        cleanup=lambda: cleanup_order.append("second"),
    )
    registry.register(
        object(),
        cleanup=lambda: cleanup_order.append("third"),
    )

    assert registry.close_all() == 3
    assert cleanup_order == ["third", "second", "first"]


def test_cleanup_failure():
    registry = ResourceRegistry()
    cleaned = []

    registry.register(
        object(),
        cleanup=lambda: cleaned.append("first"),
    )

    def failing_cleanup():
        raise RuntimeError("Cleanup failed")

    registry.register(object(), cleanup=failing_cleanup)

    registry.register(
        object(),
        cleanup=lambda: cleaned.append("last"),
    )

    try:
        registry.close_all()
        assert False, "Expected ResourceCleanupError"
    except ResourceCleanupError as exc:
        assert len(exc.errors) == 1

    assert cleaned == ["last", "first"]
    assert registry.is_closed
    assert registry.resource_count == 0


def test_cleanup_without_raising():
    registry = ResourceRegistry()

    def failing_cleanup():
        raise RuntimeError("Expected failure")

    registry.register(object(), cleanup=failing_cleanup)

    assert registry.close_all(raise_errors=False) == 1
    assert registry.is_closed


def test_context_manager():
    resource = FakeResource("client")

    with ResourceRegistry() as registry:
        registry.register(resource)
        assert registry.resource_count == 1

    assert resource.closed
    assert registry.is_closed


def test_register_after_close():
    registry = ResourceRegistry()
    registry.close_all()

    try:
        registry.register(FakeResource("late"))
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass


def test_convenience_function():
    registry = ResourceRegistry()
    resource = FakeResource("provider")

    registration = register_resource(
        registry,
        resource,
        name="custom-provider",
    )

    assert registration.resource_name == "custom-provider"
    assert registry.contains(registration.token)


if __name__ == "__main__":
    tests = [
        test_register_resource,
        test_release_resource,
        test_reverse_cleanup_order,
        test_cleanup_failure,
        test_cleanup_without_raising,
        test_context_manager,
        test_register_after_close,
        test_convenience_function,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All resource utility tests passed.")

