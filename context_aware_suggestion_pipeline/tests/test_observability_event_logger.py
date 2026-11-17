
from context_aware_suggestion_rag.observability.event_logger import (
    InMemoryEventLogger,
)


def test_event_logger_connection():
    logger = InMemoryEventLogger()

    assert logger.health_check() is False

    logger.connect()

    assert logger.health_check() is True

    print("Event logger connection: PASS")


def test_log_event():
    logger = InMemoryEventLogger()

    event = logger.log_event(
        name="pipeline.completed",
        message="Pipeline completed successfully.",
        level="info",
        attributes={"execution_id": "exec_001"},
    )

    assert event.name == "pipeline.completed"
    assert event.level == "INFO"
    assert event.attributes["execution_id"] == "exec_001"

    print("Event logging: PASS")


def test_event_filtering():
    logger = InMemoryEventLogger()

    logger.log_event("pipeline.started", "Started", "INFO")
    logger.log_event("pipeline.failed", "Failed", "ERROR")
    logger.log_event("pipeline.completed", "Completed", "INFO")

    assert logger.count() == 3
    assert logger.count("INFO") == 2
    assert logger.count("ERROR") == 1

    assert len(logger.get_events(level="INFO")) == 2
    assert len(logger.get_events(name="pipeline.failed")) == 1

    print("Event filtering: PASS")


def test_event_limit():
    logger = InMemoryEventLogger(max_events=2)

    first = logger.log_event("event.one", "First")
    logger.log_event("event.two", "Second")
    logger.log_event("event.three", "Third")

    events = logger.get_events()

    assert len(events) == 2
    assert events[0].name == "event.two"
    assert events[1].name == "event.three"
    assert logger.get_event(first.event_id) is None

    print("Event storage limit: PASS")


def test_trace_association():
    logger = InMemoryEventLogger()

    event = logger.log_event(
        name="retrieval.completed",
        message="Retrieval completed.",
        trace_id="trace_123",
        span_id="span_123",
    )

    assert event.trace_id == "trace_123"
    assert event.span_id == "span_123"

    print("Trace association: PASS")


def test_event_validation():
    logger = InMemoryEventLogger()

    try:
        logger.log_event("event.invalid", "Invalid", "UNKNOWN")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid log levels must be rejected.")

    print("Event validation: PASS")


def test_clear_and_close():
    logger = InMemoryEventLogger()

    logger.log_event("test.event", "Test")
    logger.clear()

    assert logger.count() == 0

    logger.close()

    assert logger.health_check() is False

    try:
        logger.log_event("test.event", "After close")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Closed logger must reject operations.")

    print("Event logger clear and close: PASS")


if __name__ == "__main__":
    test_event_logger_connection()
    test_log_event()
    test_event_filtering()
    test_event_limit()
    test_trace_association()
    test_event_validation()
    test_clear_and_close()

    print("All observability event logger tests passed.")
