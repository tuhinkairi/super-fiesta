
from context_aware_suggestion_rag.interfaces.observability_provider import (
    ObservabilityProvider,
    MetricsProvider,
    TracingProvider,
)


class FakeMetricsProvider(MetricsProvider):

    def __init__(self):
        self.metrics = []

    def health_check(self):
        return True

    def increment(self, name, value=1, tags=None):
        self.metrics.append(("increment", name, value, tags))

    def gauge(self, name, value, tags=None):
        self.metrics.append(("gauge", name, value, tags))

    def timing(self, name, duration_ms, tags=None):
        self.metrics.append(("timing", name, duration_ms, tags))


class FakeTracingProvider(TracingProvider):

    def health_check(self):
        return True

    def start_span(self, name, attributes=None):
        return {"name": name, "attributes": attributes or {}}

    def end_span(self, span):
        span["ended"] = True


def main():
    metrics = FakeMetricsProvider()
    tracing = FakeTracingProvider()

    assert isinstance(metrics, ObservabilityProvider)
    assert isinstance(tracing, ObservabilityProvider)
    print("Observability provider inheritance: PASS")

    assert metrics.health_check()
    assert tracing.health_check()
    print("Observability health checks: PASS")

    metrics.increment("requests", 1)
    metrics.gauge("active_users", 5)
    metrics.timing("request_duration", 125.5)

    assert len(metrics.metrics) == 3
    print("Metrics recording interfaces: PASS")

    span = tracing.start_span("pipeline.execution")
    assert span["name"] == "pipeline.execution"

    tracing.end_span(span)
    assert span["ended"] is True
    print("Tracing interfaces: PASS")

    metrics.close()
    tracing.close()
    print("Observability provider close interface: PASS")

    print("\nAll observability provider interface tests passed.")


if __name__ == "__main__":
    main()
