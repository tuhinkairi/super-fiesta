import pytest
from unittest.mock import MagicMock

from graphrag_app.pipeline.qa_pipeline import QAPipeline

from graphrag_app.retrieval.models import (
    RetrievalRequest,
    RetrievalResult,
    RetrievedEntity,
)

from graphrag_app.generation.models import GenerationResult


@pytest.fixture
def retrieval_service():
    return MagicMock()


@pytest.fixture
def answer_generator():
    return MagicMock()


@pytest.fixture
def qa_pipeline(retrieval_service, answer_generator):
    return QAPipeline(
        retrieval_service=retrieval_service,
        answer_generator=answer_generator,
    )


def test_qa_pipeline_success(
    qa_pipeline,
    retrieval_service,
    answer_generator,
):
    request = RetrievalRequest(
        query="What is Python?",
        top_k=5,
    )

    retrieval_result = RetrievalResult(
        query="What is Python?",
        entities=[
            RetrievedEntity(
                entity_id="entity-1",
                name="Python",
                entity_type="Programming Language",
                description="A high-level programming language.",
            )
        ],
        context="Python is a high-level programming language.",
        total_entities=1,
        total_relationships=0,
    )

    generation_result = GenerationResult(
        query="What is Python?",
        answer="Python is a high-level programming language.",
        model="test-model",
    )

    retrieval_service.retrieve.return_value = retrieval_result
    answer_generator.generate.return_value = generation_result

    retrieved, generated = qa_pipeline.answer(request)

    assert retrieved == retrieval_result
    assert generated == generation_result

    retrieval_service.retrieve.assert_called_once_with(request)
    answer_generator.generate.assert_called_once()


def test_qa_pipeline_passes_retrieved_context(
    qa_pipeline,
    retrieval_service,
    answer_generator,
):
    request = RetrievalRequest(query="Explain Python")

    retrieval_result = RetrievalResult(
        query="Explain Python",
        context="Python is used for programming and automation.",
    )

    retrieval_service.retrieve.return_value = retrieval_result

    answer_generator.generate.return_value = GenerationResult(
        query="Explain Python",
        answer="Python is a programming language.",
        model="test-model",
    )

    qa_pipeline.answer(request)

    generation_request = answer_generator.generate.call_args.args[0]

    assert generation_request.query == "Explain Python"
    assert (
        generation_request.context
        == "Python is used for programming and automation."
    )


def test_qa_pipeline_propagates_retrieval_error(
    qa_pipeline,
    retrieval_service,
    answer_generator,
):
    request = RetrievalRequest(query="What is Python?")

    retrieval_service.retrieve.side_effect = RuntimeError(
        "Neo4j connection failed."
    )

    with pytest.raises(RuntimeError, match="Neo4j connection failed"):
        qa_pipeline.answer(request)

    answer_generator.generate.assert_not_called()


def test_qa_pipeline_propagates_generation_error(
    qa_pipeline,
    retrieval_service,
    answer_generator,
):
    request = RetrievalRequest(query="What is Python?")

    retrieval_service.retrieve.return_value = RetrievalResult(
        query="What is Python?",
        context="Python is a programming language.",
    )

    answer_generator.generate.side_effect = RuntimeError(
        "Gemini API failed."
    )

    with pytest.raises(RuntimeError, match="Gemini API failed"):
        qa_pipeline.answer(request)
