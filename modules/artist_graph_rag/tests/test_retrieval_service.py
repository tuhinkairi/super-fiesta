from unittest.mock import MagicMock

from graphrag_app.retrieval.models import (
    RetrievalRequest,
    RetrievedEntity,
)
from graphrag_app.retrieval.service import RetrievalService


def create_entities():
    """Create sample retrieved entities."""

    return [
        RetrievedEntity(
            entity_id="entity-001",
            name="Python",
            entity_type="Programming Language",
            description="A general-purpose programming language.",
            properties={
                "difficulty": "beginner",
            },
        ),
        RetrievedEntity(
            entity_id="entity-002",
            name="Machine Learning",
            entity_type="Concept",
            description="A field of artificial intelligence.",
        ),
    ]


def create_relationships():
    """Create sample graph relationships."""

    return [
        {
            "source": "Python",
            "relationship": "USED_FOR",
            "target": "Machine Learning",
        }
    ]


def test_retrieval_service_success():
    """Test successful retrieval and context construction."""

    graph_retriever = MagicMock()

    graph_retriever.retrieve.return_value = (
        create_entities(),
        create_relationships(),
    )

    service = RetrievalService(
        graph_retriever=graph_retriever
    )

    request = RetrievalRequest(
        query="How is Python used in machine learning?"
    )

    result = service.retrieve(request)

    assert result.query == request.query

    assert result.total_entities == 2
    assert result.total_relationships == 1

    assert len(result.entities) == 2
    assert len(result.relationships) == 1

    assert "Python" in result.context
    assert "Machine Learning" in result.context
    assert "USED_FOR" in result.context

    graph_retriever.retrieve.assert_called_once_with(
        request
    )


def test_retrieval_service_empty_results():
    """Test retrieval when no graph information is found."""

    graph_retriever = MagicMock()

    graph_retriever.retrieve.return_value = ([], [])

    service = RetrievalService(
        graph_retriever=graph_retriever
    )

    request = RetrievalRequest(
        query="Unknown technology"
    )

    result = service.retrieve(request)

    assert result.entities == []
    assert result.relationships == []

    assert result.total_entities == 0
    assert result.total_relationships == 0

    assert (
        result.context
        == "No relevant knowledge was found in the knowledge graph."
    )


def test_context_contains_entity_properties():
    """Test that entity properties are included in context."""

    graph_retriever = MagicMock()

    graph_retriever.retrieve.return_value = (
        create_entities(),
        [],
    )

    service = RetrievalService(
        graph_retriever=graph_retriever
    )

    request = RetrievalRequest(query="Python")

    result = service.retrieve(request)

    assert "difficulty=beginner" in result.context


def test_context_contains_relationship_direction():
    """Test that relationship direction is preserved."""

    graph_retriever = MagicMock()

    graph_retriever.retrieve.return_value = (
        create_entities(),
        create_relationships(),
    )

    service = RetrievalService(
        graph_retriever=graph_retriever
    )

    request = RetrievalRequest(query="Python")

    result = service.retrieve(request)

    assert (
        "Python --[USED_FOR]--> Machine Learning"
        in result.context
    )
