from datetime import timedelta

from context_aware_suggestion_rag.observability.models import (
    MetricRecord,
    MetricType,
    ObservabilityEvent,
    SpanStatus,
    TraceSpan,
    current_utc_time,
)


def test_metric_record():
    metric = MetricRecord(
        name="pipeline.requests",
        metric_type=MetricType.COUNTER,
        value=10,
        description="Total pipeline requests",
        labels={"environment": "test"},
    )

    assert metric.name == "pipeline.requests"
    assert metric.value == 10.0
    assert metric.metric_type == MetricType.COUNTER
    assert metric.labels["environment"] == "test"

    print("Metric record: PASS")


def test_metric_validation():
    try:
        MetricRecord(
            name="",
            metric_type=MetricType.COUNTER,
            value=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Empty metric name should be rejected.")

    try:
        MetricRecord(
            name="invalid.metric",
            metric_type=MetricType.GAUGE,
            value=float("nan"),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Non-finite metric values should be rejected.")

    print("Metric validation: PASS")


def test_trace_span():
    start = current_utc_time()

    span = TraceSpan(
        name="document.ingestion",
        started_at=start,
        ended_at=start + timedelta(seconds=2),
        status=SpanStatus.OK,
        attributes={"document_type": "pdf"},
    )

    assert span.is_completed is True
    assert span.duration_ms == 2000.0
    assert span.status == SpanStatus.OK

    print("Trace span: PASS")


def test_trace_span_validation():
    start = current_utc_time()

    try:
        TraceSpan(
            name="invalid.span",
            started_at=start,
            ended_at=start - timedelta(seconds=1),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid span timing should be rejected.")

    print("Trace span validation: PASS")


def test_observability_event():
    event = ObservabilityEvent(
        name="pipeline.completed",
        message="Pipeline execution completed successfully.",
        level="info",
        attributes={"execution_id": "exec_123"},
    )

    assert event.name == "pipeline.completed"
    assert event.level == "INFO"
    assert event.attributes["execution_id"] == "exec_123"
    assert event.event_id.startswith("evt_")

    print("Observability event: PASS")


if __name__ == "__main__":
    test_metric_record()
    test_metric_validation()
    test_trace_span()
    test_trace_span_validation()
    test_observability_event()

    print("All observability model tests passed.")
