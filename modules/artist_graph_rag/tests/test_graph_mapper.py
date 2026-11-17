
import pytest

from graphrag_app.extraction.models import (
    ChunkExtractionResult,
    ExtractedEntity,
    ExtractedRelationship,
)
from graphrag_app.graph.mapper import GraphMapper


@pytest.fixture
def sample_extraction():
    return ChunkExtractionResult(
        document_id="doc-001",
        chunk_id="chunk-001",
        entities=[
            ExtractedEntity(
                name="Python",
                entity_type="Programming Language",
                description="A high-level programming language.",
                properties={"paradigm": "Multi-paradigm"},
            ),
            ExtractedEntity(
                name="Machine Learning",
                entity_type="AI Concept",
                description="A field of artificial intelligence.",
            ),
        ],
        relationships=[
            ExtractedRelationship(
                source_entity_name="Python",
                target_entity_name="Machine Learning",
                relation_type="USED_FOR",
                description="Python is used in Machine Learning.",
            )
        ],
    )


def test_map_entities(sample_extraction):
    """Test conversion of extracted entities into graph entities."""

    mapper = GraphMapper()

    entities, relationships = mapper.map_extraction(
        sample_extraction
    )

    assert len(entities) == 2

    python_entity = next(
        entity for entity in entities
        if entity.name == "Python"
    )

    assert python_entity.entity_type == "Programming Language"
    assert python_entity.source_document_id == "doc-001"
    assert python_entity.source_chunk_id == "chunk-001"
    assert python_entity.properties["paradigm"] == "Multi-paradigm"

    assert relationships[0].source_entity_id == python_entity.id


def test_map_relationships(sample_extraction):
    """Test conversion of extracted relationships into graph relationships."""

    mapper = GraphMapper()

    entities, relationships = mapper.map_extraction(
        sample_extraction
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    entity_names = {
        entity.id: entity.name
        for entity in entities
    }

    assert entity_names[relationship.source_entity_id] == "Python"
    assert entity_names[relationship.target_entity_id] == "Machine Learning"

    assert relationship.relation_type == "USED_FOR"
    assert relationship.source_document_id == "doc-001"


def test_entity_ids_are_deterministic(sample_extraction):
    """Test that identical entities receive identical IDs."""

    mapper = GraphMapper()

    entities_first, _ = mapper.map_extraction(
        sample_extraction
    )

    entities_second, _ = mapper.map_extraction(
        sample_extraction
    )

    first_ids = [entity.id for entity in entities_first]
    second_ids = [entity.id for entity in entities_second]

    assert first_ids == second_ids


def test_entity_ids_are_consistent_across_chunks():
    """Test that the same normalized entity gets the same ID."""

    mapper = GraphMapper()

    first_result = ChunkExtractionResult(
        document_id="doc-001",
        chunk_id="chunk-001",
        entities=[
            ExtractedEntity(
                name="Python",
                entity_type="Programming Language",
            )
        ],
    )

    second_result = ChunkExtractionResult(
        document_id="doc-001",
        chunk_id="chunk-002",
        entities=[
            ExtractedEntity(
                name=" python ",
                entity_type="Programming Language",
            )
        ],
    )

    first_entities, _ = mapper.map_extraction(first_result)
    second_entities, _ = mapper.map_extraction(second_result)

    assert first_entities[0].id == second_entities[0].id


def test_unknown_relationship_entities_are_skipped():
    """Test that unresolved relationship endpoints are ignored."""

    result = ChunkExtractionResult(
        document_id="doc-001",
        chunk_id="chunk-001",
        entities=[
            ExtractedEntity(
                name="Python",
                entity_type="Programming Language",
            )
        ],
        relationships=[
            ExtractedRelationship(
                source_entity_name="Python",
                target_entity_name="Unknown",
                relation_type="RELATED_TO",
            )
        ],
    )

    mapper = GraphMapper()

    entities, relationships = mapper.map_extraction(result)

    assert len(entities) == 1
    assert relationships == []


def test_empty_extraction():
    """Test mapping an extraction result without entities."""

    result = ChunkExtractionResult(
        document_id="doc-001",
        chunk_id="chunk-001",
    )

    mapper = GraphMapper()

    entities, relationships = mapper.map_extraction(result)

    assert entities == []
    assert relationships == []
