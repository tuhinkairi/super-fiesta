
from context_aware_suggestion_rag.observability.factory import (
    create_application_monitor,
    create_event_logger,
    create_metrics_provider,
    create_tracing_provider,
)
from context_aware_suggestion_rag.observability.metrics import (
    InMemoryMetricsProvider,
)
from context_aware_suggestion_rag.observability.tracing import (
    InMemoryTracingProvider,
)
from context_aware_suggestion_rag.observability.event_logger import (
    InMemoryEventLogger,
)
from context_aware_suggestion_rag.observability.monitoring import (
    ApplicationMonitor,
)


def test_create_metrics_provider():
    provider = create_metrics_provider(max_records=100)

    assert isinstance(provider, InMemoryMetricsProvider)

    provider.connect()
    assert provider.health_check() is True

    print("Metrics provider factory: PASS")


def test_create_tracing_provider():
    provider = create_tracing_provider(max_spans=100)

    assert isinstance(provider, InMemoryTracingProvider)

    provider.connect()
    assert provider.health_check() is True

    print("Tracing provider factory: PASS")


def test_create_event_logger():
    logger = create_event_logger(max_events=100)

    assert isinstance(logger, InMemoryEventLogger)

    logger.connect()
    assert logger.health_check() is True

    print("Event logger factory: PASS")


def test_create_application_monitor():
    monitor = create_application_monitor()

    assert isinstance(monitor, ApplicationMonitor)

    monitor.connect()
    assert monitor.health_check() is True

    print("Application monitor factory: PASS")


def test_create_monitor_with_custom_providers():
    metrics = create_metrics_provider(max_records=50)
    tracing = create_tracing_provider(max_spans=50)
    logger = create_event_logger(max_events=50)

    monitor = create_application_monitor(
        metrics_provider=metrics,
        tracing_provider=tracing,
        event_logger=logger,
    )

    monitor.connect()
    assert monitor.health_check() is True

    print("Custom observability providers: PASS")


if __name__ == "__main__":
    test_create_metrics_provider()
    test_create_tracing_provider()
    test_create_event_logger()
    test_create_application_monitor()
    test_create_monitor_with_custom_providers()

    print("All observability factory tests passed.")
