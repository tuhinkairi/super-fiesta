
from unittest.mock import MagicMock

from graphrag_app.extraction.models import (
    ChunkExtractionResult,
    ExtractedEntity,
    ExtractedRelationship,
)
from graphrag_app.graph.ingestion_service import (
    GraphIngestionService,
)
from graphrag_app.graph.schema import Entity, Relationship


def create_extraction_result():
    """Create sample extraction data for testing."""

    return ChunkExtractionResult(
        document_id="document-001",
        chunk_id="chunk-001",
        entities=[
            ExtractedEntity(
                name="Python",
                entity_type="Programming Language",
                description="A programming language.",
            ),
            ExtractedEntity(
                name="Machine Learning",
                entity_type="Concept",
                description="A field of artificial intelligence.",
            ),
        ],
        relationships=[
            ExtractedRelationship(
                source_entity_name="Python",
                target_entity_name="Machine Learning",
                relation_type="USED_FOR",
                description="Python is used for machine learning.",
            )
        ],
    )


def test_store_extraction():
    """Test mapping and storage of extraction results."""

    mapper = MagicMock()
    graph_service = MagicMock()

    entities = [
        Entity(
            id="entity-001",
            name="Python",
            entity_type="Programming Language",
        )
    ]

    relationships = [
        Relationship(
            id="relationship-001",
            source_entity_id="entity-001",
            target_entity_id="entity-002",
            relation_type="USED_FOR",
        )
    ]

    mapper.map_extraction.return_value = (
        entities,
        relationships,
    )

    graph_service.store_graph.return_value = {
        "entities_stored": 1,
        "relationships_stored": 1,
    }

    service = GraphIngestionService(
        graph_service=graph_service,
        mapper=mapper,
    )

    extraction = create_extraction_result()

    result = service.store_extraction(extraction)

    mapper.map_extraction.assert_called_once_with(
        extraction
    )

    graph_service.store_graph.assert_called_once_with(
        entities=entities,
        relationships=relationships,
    )

    assert result == {
        "entities_stored": 1,
        "relationships_stored": 1,
    }


def test_store_empty_extraction():
    """Test storage when extraction contains no entities."""

    mapper = MagicMock()
    graph_service = MagicMock()

    mapper.map_extraction.return_value = ([], [])

    graph_service.store_graph.return_value = {
        "entities_stored": 0,
        "relationships_stored": 0,
    }

    service = GraphIngestionService(
        graph_service=graph_service,
        mapper=mapper,
    )

    extraction = ChunkExtractionResult(
        document_id="document-002",
        chunk_id="chunk-002",
    )

    result = service.store_extraction(extraction)

    graph_service.store_graph.assert_called_once_with(
        entities=[],
        relationships=[],
    )

    assert result["entities_stored"] == 0
    assert result["relationships_stored"] == 0
