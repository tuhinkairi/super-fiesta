
from context_aware_suggestion_rag.observability.metrics import (
    InMemoryMetricsProvider,
)
from context_aware_suggestion_rag.observability.models import MetricType


def test_metrics_connection():
    provider = InMemoryMetricsProvider()
    assert provider.health_check() is False

    provider.connect()

    assert provider.health_check() is True

    print("Metrics connection: PASS")


def test_counter_metrics():
    provider = InMemoryMetricsProvider()
    provider.connect()

    first = provider.increment("pipeline.requests")
    second = provider.increment("pipeline.requests", 2)

    assert first.value == 1.0
    assert second.value == 3.0
    assert second.metric_type == MetricType.COUNTER
    assert provider.get_counter_value("pipeline.requests") == 3.0

    print("Counter metrics: PASS")


def test_gauge_and_timing():
    provider = InMemoryMetricsProvider()
    provider.connect()

    gauge = provider.gauge("system.memory", 75.5)
    timing = provider.timing("pipeline.duration", 250.0)

    assert gauge.value == 75.5
    assert gauge.metric_type == MetricType.GAUGE

    assert timing.value == 250.0
    assert timing.metric_type == MetricType.TIMING

    print("Gauge and timing metrics: PASS")


def test_metric_filtering():
    provider = InMemoryMetricsProvider()
    provider.connect()

    provider.increment("requests")
    provider.gauge("memory", 50)
    provider.increment("requests", 2)

    assert len(provider.get_metrics()) == 3
    assert len(provider.get_metrics("requests")) == 2
    assert len(provider.get_metrics("memory")) == 1

    print("Metric filtering: PASS")


def test_metric_validation():
    provider = InMemoryMetricsProvider()
    provider.connect()

    try:
        provider.increment("requests", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative counter increments must be rejected.")

    try:
        provider.timing("duration", -10)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative timings must be rejected.")

    print("Metric validation: PASS")


def test_record_limit_and_clear():
    provider = InMemoryMetricsProvider(max_records=2)
    provider.connect()

    provider.increment("a")
    provider.increment("b")
    provider.increment("c")

    assert len(provider.get_metrics()) == 2

    provider.clear()

    assert len(provider.get_metrics()) == 0
    assert provider.get_counter_value("a") == 0.0

    print("Metric record limit and clearing: PASS")


def test_close():
    provider = InMemoryMetricsProvider()
    provider.connect()
    provider.close()

    assert provider.health_check() is False

    try:
        provider.increment("requests")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Closed provider must reject operations.")

    print("Metrics provider close: PASS")


if __name__ == "__main__":
    test_metrics_connection()
    test_counter_metrics()
    test_gauge_and_timing()
    test_metric_filtering()
    test_metric_validation()
    test_record_limit_and_clear()
    test_close()

    print("All observability metrics tests passed.")
