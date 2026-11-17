
from context_aware_suggestion_rag.observability.models import SpanStatus
from context_aware_suggestion_rag.observability.tracing import (
    InMemoryTracingProvider,
)


def test_tracing_connection():
    provider = InMemoryTracingProvider()

    assert provider.health_check() is False

    provider.connect()

    assert provider.health_check() is True

    print("Tracing connection: PASS")


def test_start_and_end_span():
    provider = InMemoryTracingProvider()

    span = provider.start_span(
        "document.ingestion",
        attributes={"document_type": "pdf"},
    )

    assert span.name == "document.ingestion"
    assert span.is_completed is False

    completed = provider.end_span(span.span_id, status="ok")

    assert completed.is_completed is True
    assert completed.status == SpanStatus.OK
    assert completed.duration_ms is not None

    print("Start and end span: PASS")


def test_parent_child_relationship():
    provider = InMemoryTracingProvider()

    parent = provider.start_span("pipeline")

    child = provider.start_span(
        "document.processing",
        parent_span_id=parent.span_id,
    )

    assert child.parent_span_id == parent.span_id
    assert child.trace_id == parent.trace_id

    trace = provider.get_trace(parent.trace_id)

    assert len(trace) == 2

    print("Parent-child relationships: PASS")


def test_span_events_and_attributes():
    provider = InMemoryTracingProvider()

    span = provider.start_span("retrieval")

    updated = provider.set_attribute(
        span.span_id,
        "namespace",
        "documents",
    )

    assert updated.attributes["namespace"] == "documents"

    updated = provider.add_event(
        span.span_id,
        "retrieval.completed",
        {"matches": 5},
    )

    assert len(updated.events) == 1
    assert updated.events[0]["name"] == "retrieval.completed"

    print("Span events and attributes: PASS")


def test_error_span():
    provider = InMemoryTracingProvider()

    span = provider.start_span("generation")

    completed = provider.end_span(
        span.span_id,
        status="error",
        error="Generation failed",
    )

    assert completed.status == SpanStatus.ERROR
    assert completed.error == "Generation failed"

    print("Error span: PASS")


def test_span_validation():
    provider = InMemoryTracingProvider()

    try:
        provider.start_span("")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty span names must be rejected.")

    parent = provider.start_span("parent")
    provider.end_span(parent.span_id)

    try:
        provider.start_span(
            "child",
            parent_span_id=parent.span_id,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Ended parent spans must be rejected.")

    print("Span validation: PASS")


def test_clear_and_close():
    provider = InMemoryTracingProvider()

    provider.start_span("pipeline")
    assert provider.get_span_count() == 1

    provider.clear()
    assert provider.get_span_count() == 0

    provider.close()
    assert provider.health_check() is False

    print("Tracing clear and close: PASS")


if __name__ == "__main__":
    test_tracing_connection()
    test_start_and_end_span()
    test_parent_child_relationship()
    test_span_events_and_attributes()
    test_error_span()
    test_span_validation()
    test_clear_and_close()

    print("All observability tracing tests passed.")
