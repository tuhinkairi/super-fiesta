
from context_aware_suggestion_rag.observability.models import SpanStatus
from context_aware_suggestion_rag.observability.monitoring import (
    ApplicationMonitor,
)


def test_monitor_connection():
    monitor = ApplicationMonitor()

    assert monitor.health_check() is False

    monitor.connect()

    assert monitor.health_check() is True

    print("Application monitor connection: PASS")


def test_pipeline_start():
    monitor = ApplicationMonitor()

    span = monitor.record_pipeline_start(
        "suggestion_pipeline",
        "exec_001",
    )

    assert span.name == "pipeline.suggestion_pipeline"
    assert span.attributes["execution_id"] == "exec_001"

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0

    print("Pipeline start tracking: PASS")


def test_pipeline_success():
    monitor = ApplicationMonitor()

    span = monitor.record_pipeline_start(
        "suggestion_pipeline",
        "exec_002",
    )

    completed = monitor.record_pipeline_success(
        span.span_id,
        execution_time_ms=250.0,
    )

    assert completed.status == SpanStatus.OK
    assert completed.is_completed is True

    metrics = monitor.get_pipeline_metrics()

    assert metrics["started"] == 1.0
    assert metrics["completed"] == 1.0
    assert metrics["failed"] == 0.0

    print("Pipeline success tracking: PASS")


def test_pipeline_failure():
    monitor = ApplicationMonitor()

    span = monitor.record_pipeline_start(
        "suggestion_pipeline",
        "exec_003",
    )

    failed = monitor.record_pipeline_failure(
        span.span_id,
        error="Document ingestion failed.",
        execution_time_ms=150.0,
    )

    assert failed.status == SpanStatus.ERROR
    assert failed.error == "Document ingestion failed."

    metrics = monitor.get_pipeline_metrics()

    assert metrics["failed"] == 1.0

    print("Pipeline failure tracking: PASS")


def test_custom_event():
    monitor = ApplicationMonitor()

    event = monitor.record_custom_event(
        name="document.uploaded",
        message="A document was uploaded.",
        attributes={"document_type": "pdf"},
    )

    assert event.name == "document.uploaded"
    assert event.attributes["document_type"] == "pdf"

    print("Custom event tracking: PASS")


def test_monitor_validation():
    monitor = ApplicationMonitor()

    try:
        monitor.record_pipeline_start("", "exec_001")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty pipeline names must be rejected.")

    span = monitor.record_pipeline_start(
        "pipeline",
        "exec_004",
    )

    try:
        monitor.record_pipeline_success(
            span.span_id,
            execution_time_ms=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Negative execution time must be rejected.")

    print("Monitor validation: PASS")


def test_close():
    monitor = ApplicationMonitor()
    monitor.connect()
    monitor.close()

    assert monitor.health_check() is False

    print("Application monitor close: PASS")


if __name__ == "__main__":
    test_monitor_connection()
    test_pipeline_start()
    test_pipeline_success()
    test_pipeline_failure()
    test_custom_event()
    test_monitor_validation()
    test_close()

    print("All observability monitoring tests passed.")
