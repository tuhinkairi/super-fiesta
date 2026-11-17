
import asyncio

from context_aware_suggestion_rag.observability.decorators import (
    observe,
    observe_method,
)
from context_aware_suggestion_rag.observability.monitoring import (
    ApplicationMonitor,
)


def test_observe_success():
    monitor = ApplicationMonitor()

    @observe(monitor=monitor, pipeline_name="test.success")
    def sample_function(value):
        return value * 2

    result = sample_function(5)

    assert result == 10

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0
    assert metrics["completed"] == 1.0
    assert metrics["failed"] == 0.0

    print("Successful function observation: PASS")


def test_observe_failure():
    monitor = ApplicationMonitor()

    @observe(monitor=monitor, pipeline_name="test.failure")
    def failing_function():
        raise ValueError("Expected failure")

    try:
        failing_function()
    except ValueError as exc:
        assert str(exc) == "Expected failure"
    else:
        raise AssertionError("Original exception must propagate.")

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0
    assert metrics["failed"] == 1.0
    assert metrics["completed"] == 0.0

    print("Failed function observation: PASS")


def test_observe_without_monitor():
    @observe
    def sample_function():
        return "success"

    assert sample_function() == "success"

    print("Observation without monitor: PASS")


def test_observe_method():
    monitor = ApplicationMonitor()

    class SampleService:
        def __init__(self):
            self.monitor = monitor

        @observe_method(pipeline_name="sample.method")
        def execute(self, value):
            return value + 1

    service = SampleService()

    assert service.execute(10) == 11

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0
    assert metrics["completed"] == 1.0

    print("Method observation: PASS")


def test_async_observe():
    monitor = ApplicationMonitor()

    @observe(monitor=monitor, pipeline_name="test.async")
    async def async_function(value):
        return value * 3

    result = asyncio.run(async_function(4))

    assert result == 12

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0
    assert metrics["completed"] == 1.0

    print("Async function observation: PASS")


def test_decorator_preserves_metadata():
    @observe
    def documented_function():
        """Example function documentation."""
        return True

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "Example function documentation."
    assert documented_function() is True

    print("Decorator metadata preservation: PASS")


if __name__ == "__main__":
    test_observe_success()
    test_observe_failure()
    test_observe_without_monitor()
    test_observe_method()
    test_async_observe()
    test_decorator_preserves_metadata()

    print("All observability decorator tests passed.")
