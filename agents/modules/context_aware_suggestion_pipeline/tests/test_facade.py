
"""Tests for the public pipeline facade."""

from context_aware_suggestion_rag.facade import (
    ContextAwareSuggestionFacade,
)
from context_aware_suggestion_rag.pipeline import (
    ContextAwareSuggestionPipeline,
    PipelineStage,
    PipelineStatus,
)
from context_aware_suggestion_rag.exceptions import WorkflowError


def sample_stage(state):
    return {"processed": True}


def failing_stage(state):
    raise RuntimeError("Simulated failure")


def create_facade():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("processing", sample_stage),
        ]
    )

    return ContextAwareSuggestionFacade(pipeline)


def test_execute():
    facade = create_facade()

    result = facade.execute({"document": "Test document"})

    assert result.status == PipelineStatus.COMPLETED
    assert result.output_data["processed"] is True

    print("Facade execution: PASS")


def test_execute_or_raise():
    facade = create_facade()

    result = facade.execute_or_raise(
        {"document": "Test document"}
    )

    assert result.is_successful

    print("Facade execute-or-raise: PASS")


def test_stage_names():
    facade = create_facade()

    assert facade.get_stage_names() == ("processing",)

    print("Facade stage listing: PASS")


def test_health_check():
    facade = create_facade()

    assert facade.health_check() is True

    facade.close()

    assert facade.health_check() is False

    print("Facade health check: PASS")


def test_closed_facade():
    facade = create_facade()
    facade.close()

    try:
        facade.execute({"document": "Test"})
    except WorkflowError:
        pass
    else:
        raise AssertionError("Expected WorkflowError.")

    print("Closed facade protection: PASS")


def test_failed_execution_raises():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("failure", failing_stage),
        ]
    )

    facade = ContextAwareSuggestionFacade(pipeline)

    try:
        facade.execute_or_raise({"document": "Test"})
    except WorkflowError:
        pass
    else:
        raise AssertionError("Expected WorkflowError.")

    print("Facade failure propagation: PASS")


if __name__ == "__main__":
    test_execute()
    test_execute_or_raise()
    test_stage_names()
    test_health_check()
    test_closed_facade()
    test_failed_execution_raises()

    print("\nAll facade tests passed.")
