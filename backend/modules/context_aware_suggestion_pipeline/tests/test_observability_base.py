from context_aware_suggestion_rag.observability.base import (
    BaseEventLogger,
    BaseMetricsProvider,
    BaseObservabilityProvider,
    BaseTracingProvider,
)


def test_abstract_classes():
    assert BaseObservabilityProvider.__abstractmethods__ == {
        "connect",
        "health_check",
    }

    assert BaseMetricsProvider.__abstractmethods__ == {
        "connect",
        "health_check",
        "increment",
        "gauge",
        "timing",
        "get_metrics",
    }

    assert BaseTracingProvider.__abstractmethods__ == {
        "connect",
        "health_check",
        "start_span",
        "end_span",
        "get_span",
        "get_trace",
    }

    assert BaseEventLogger.__abstractmethods__ == {
        "connect",
        "health_check",
        "log_event",
        "get_events",
    }

    print("Observability abstract interfaces: PASS")


def test_abstract_instantiation():
    for provider_class in (
        BaseObservabilityProvider,
        BaseMetricsProvider,
        BaseTracingProvider,
        BaseEventLogger,
    ):
        try:
            provider_class()
        except TypeError:
            continue
        else:
            raise AssertionError(
                f"{provider_class.__name__} should not be instantiated."
            )

    print("Abstract instantiation protection: PASS")


if __name__ == "__main__":
    test_abstract_classes()
    test_abstract_instantiation()

    print("All observability base tests passed.")
