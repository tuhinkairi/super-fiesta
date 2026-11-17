
from context_aware_suggestion_rag.observability import (
    MetricType,
    SpanStatus,
    MetricRecord,
    TraceSpan,
    ObservabilityEvent,
    BaseObservabilityProvider,
    BaseMetricsProvider,
    BaseTracingProvider,
    BaseEventLogger,
    InMemoryMetricsProvider,
    InMemoryTracingProvider,
    InMemoryEventLogger,
    ApplicationMonitor,
    observe,
    observe_method,
    create_metrics_provider,
    create_tracing_provider,
    create_event_logger,
    create_application_monitor,
)


def test_model_exports():
    assert MetricType.COUNTER.value == "counter"
    assert SpanStatus.OK.value == "ok"

    print("Observability model exports: PASS")


def test_base_exports():
    assert BaseObservabilityProvider is not None
    assert BaseMetricsProvider is not None
    assert BaseTracingProvider is not None
    assert BaseEventLogger is not None

    print("Observability base exports: PASS")


def test_provider_exports():
    assert InMemoryMetricsProvider is not None
    assert InMemoryTracingProvider is not None
    assert InMemoryEventLogger is not None
    assert ApplicationMonitor is not None

    print("Observability provider exports: PASS")


def test_decorator_exports():
    assert callable(observe)
    assert callable(observe_method)

    print("Observability decorator exports: PASS")


def test_factory_exports():
    assert callable(create_metrics_provider)
    assert callable(create_tracing_provider)
    assert callable(create_event_logger)
    assert callable(create_application_monitor)

    print("Observability factory exports: PASS")


def test_all_exports():
    import context_aware_suggestion_rag.observability as package

    assert len(package.__all__) == len(set(package.__all__))

    for name in package.__all__:
        assert hasattr(package, name), f"Missing export: {name}"

    print("Observability __all__ validation: PASS")


if __name__ == "__main__":
    test_model_exports()
    test_base_exports()
    test_provider_exports()
    test_decorator_exports()
    test_factory_exports()
    test_all_exports()

    print("All observability package tests passed.")
