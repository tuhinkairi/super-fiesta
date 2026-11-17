from unittest.mock import MagicMock

from graphrag_app.retrieval.graph_retriever import GraphRetriever
from graphrag_app.retrieval.models import (
    RetrievalRequest,
    RetrievedEntity,
)


def create_mock_client():
    """Create a mocked Neo4j client."""

    client = MagicMock()

    client.execute_query.return_value = [
        {
            "entity_id": "entity-001",
            "name": "Python",
            "entity_type": "Programming Language",
            "description": "A general-purpose programming language.",
            "properties": {
                "id": "entity-001",
                "name": "Python",
                "entity_type": "Programming Language",
                "description": "A general-purpose programming language.",
                "difficulty": "beginner",
            },
            "source_document_id": "document-001",
            "source_chunk_id": "chunk-001",
            "relationships": [
                {
                    "source": "Python",
                    "relationship": "USED_FOR",
                    "target": "Machine Learning",
                }
            ],
        }
    ]

    return client


def test_retrieve_entities_and_relationships():
    """Test successful graph retrieval."""

    client = create_mock_client()
    retriever = GraphRetriever(client)

    request = RetrievalRequest(
        query="Python",
        top_k=10,
    )

    entities, relationships = retriever.retrieve(request)

    assert len(entities) == 1
    assert isinstance(entities[0], RetrievedEntity)

    assert entities[0].name == "Python"
    assert entities[0].entity_type == "Programming Language"

    assert entities[0].properties == {
        "difficulty": "beginner"
    }

    assert len(relationships) == 1

    assert relationships[0]["source"] == "Python"
    assert relationships[0]["relationship"] == "USED_FOR"
    assert relationships[0]["target"] == "Machine Learning"

    client.execute_query.assert_called_once()


def test_retrieve_with_document_filter():
    """Test that document filtering is passed to Neo4j."""

    client = create_mock_client()
    retriever = GraphRetriever(client)

    request = RetrievalRequest(
        query="Python",
        document_id="document-001",
    )

    retriever.retrieve(request)

    _, parameters = client.execute_query.call_args.args

    assert parameters["document_id"] == "document-001"


def test_retrieve_no_results():
    """Test retrieval when Neo4j returns no matching entities."""

    client = MagicMock()
    client.execute_query.return_value = []

    retriever = GraphRetriever(client)

    request = RetrievalRequest(
        query="UnknownTechnology",
    )

    entities, relationships = retriever.retrieve(request)

    assert entities == []
    assert relationships == []


def test_duplicate_relationships_are_removed():
    """Test that duplicate relationships are returned only once."""

    client = MagicMock()

    client.execute_query.return_value = [
        {
            "entity_id": "entity-001",
            "name": "Python",
            "entity_type": "Programming Language",
            "description": None,
            "properties": {},
            "source_document_id": None,
            "source_chunk_id": None,
            "relationships": [
                {
                    "source": "Python",
                    "relationship": "USED_FOR",
                    "target": "Machine Learning",
                },
                {
                    "source": "Python",
                    "relationship": "USED_FOR",
                    "target": "Machine Learning",
                },
            ],
        }
    ]

    retriever = GraphRetriever(client)

    request = RetrievalRequest(query="Python")

    entities, relationships = retriever.retrieve(request)

    assert len(entities) == 1
    assert len(relationships) == 1
