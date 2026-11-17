
"""Tests for the main pipeline coordinator."""

from context_aware_suggestion_rag.pipeline import (
    ContextAwareSuggestionPipeline,
    PipelineStage,
    PipelineStatus,
)


def extract_context(state):
    return {"context": f"Extracted: {state['document']}"}


def collect_intelligence(state):
    return {"trends": ["AI", "RAG"]}


def generate_recommendations(state):
    return {"recommendations": ["Create an AI article"]}


def failing_stage(state):
    raise RuntimeError("Simulated stage failure")


def test_successful_pipeline():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("context", extract_context),
            PipelineStage("intelligence", collect_intelligence),
            PipelineStage("recommendations", generate_recommendations),
        ]
    )

    result = pipeline.run({"document": "Artificial intelligence"})

    assert result.status == PipelineStatus.COMPLETED
    assert result.is_successful
    assert result.successful_stages == 3
    assert result.failed_stages == 0
    assert "context" in result.output_data
    assert "trends" in result.output_data
    assert "recommendations" in result.output_data

    print("Successful pipeline execution: PASS")


def test_failed_pipeline():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("context", extract_context),
            PipelineStage("failure", failing_stage),
            PipelineStage("recommendations", generate_recommendations),
        ]
    )

    result = pipeline.run({"document": "Test document"})

    assert result.status == PipelineStatus.FAILED
    assert result.failed_stages == 1
    assert result.error is not None
    assert "recommendations" not in result.output_data

    print("Failed pipeline execution: PASS")


def test_optional_stage_failure():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("context", extract_context),
            PipelineStage("optional", failing_stage, required=False),
            PipelineStage("recommendations", generate_recommendations),
        ]
    )

    result = pipeline.run({"document": "Test document"})

    assert result.status == PipelineStatus.COMPLETED
    assert result.failed_stages == 1
    assert result.successful_stages == 2
    assert "recommendations" in result.output_data

    print("Optional stage failure handling: PASS")


def test_stage_order():
    pipeline = ContextAwareSuggestionPipeline(
        stages=[
            PipelineStage("context", extract_context),
            PipelineStage("intelligence", collect_intelligence),
        ]
    )

    assert pipeline.get_stage_names() == (
        "context",
        "intelligence",
    )

    print("Pipeline stage ordering: PASS")


if __name__ == "__main__":
    test_successful_pipeline()
    test_failed_pipeline()
    test_optional_stage_failure()
    test_stage_order()

    print("\nAll pipeline tests passed.")
