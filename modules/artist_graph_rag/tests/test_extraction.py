
from unittest.mock import MagicMock

import pytest

from graphrag_app.chunking.models import DocumentChunk
from graphrag_app.extraction import (
    ExtractedEntity,
    ExtractedRelationship,
    EntityExtractor,
    RelationshipExtractor,
    ExtractionService,
)
from graphrag_app.extraction.entity_extractor import (
    EntityExtractionResponse,
)
from graphrag_app.extraction.relationship_extractor import (
    RelationshipExtractionResponse,
)


@pytest.fixture
def sample_chunk():
    return DocumentChunk(
        document_id="doc-001",
        chunk_index=0,
        text="Python is widely used in Machine Learning.",
        start_char=0,
        end_char=45,
        character_count=45,
    )


@pytest.fixture
def mock_gemini():
    """Create a mocked Gemini client compatible with LangChain."""

    client = MagicMock()
    client.model = "test-model"

    # Default entity extraction response
    client._model.with_structured_output.return_value.invoke.return_value = (
        EntityExtractionResponse(entities=[])
    )

    return client


# ============================================================
# ENTITY EXTRACTION TESTS
# ============================================================

def test_entity_extraction(sample_chunk, mock_gemini):
    """Test successful entity extraction."""

    expected_entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
            description="A programming language.",
            properties={},
        ),
        ExtractedEntity(
            name="Machine Learning",
            entity_type="AI Concept",
            description="A field of artificial intelligence.",
            properties={},
        ),
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        EntityExtractionResponse(entities=expected_entities)
    )

    extractor = EntityExtractor(mock_gemini)
    entities = extractor.extract(sample_chunk)

    assert len(entities) == 2
    assert entities[0].name == "Python"
    assert entities[1].name == "Machine Learning"


def test_entity_deduplication(sample_chunk, mock_gemini):
    """Test duplicate entities are removed."""

    duplicate_entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
            description="A programming language.",
        ),
        ExtractedEntity(
            name="python",
            entity_type="programming language",
            description="Another description.",
        ),
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        EntityExtractionResponse(entities=duplicate_entities)
    )

    extractor = EntityExtractor(mock_gemini)
    entities = extractor.extract(sample_chunk)

    assert len(entities) == 1
    assert entities[0].name == "Python"


def test_empty_entity_response(sample_chunk, mock_gemini):
    """Test that an empty entity list is accepted."""

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        EntityExtractionResponse(entities=[])
    )

    extractor = EntityExtractor(mock_gemini)
    entities = extractor.extract(sample_chunk)

    assert entities == []


def test_invalid_entity_json(sample_chunk, mock_gemini):
    """Test invalid structured entity response handling."""

    mock_gemini._model.with_structured_output.return_value.invoke.side_effect = (
        ValueError("invalid JSON")
    )

    extractor = EntityExtractor(mock_gemini)

    with pytest.raises(
        RuntimeError,
        match="Entity extraction failed",
    ):
        extractor.extract(sample_chunk)


def test_empty_entity_response_text(sample_chunk, mock_gemini):
    """Test unexpected empty entity response handling."""

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        None
    )

    extractor = EntityExtractor(mock_gemini)

    with pytest.raises(
        RuntimeError,
        match="unexpected entity response",
    ):
        extractor.extract(sample_chunk)


# ============================================================
# RELATIONSHIP EXTRACTION TESTS
# ============================================================

def test_relationship_extraction(sample_chunk, mock_gemini):
    """Test successful relationship extraction."""

    entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
        ),
        ExtractedEntity(
            name="Machine Learning",
            entity_type="AI Concept",
        ),
    ]

    expected_relationships = [
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Machine Learning",
            relation_type="USED_FOR",
            description="Python is used in Machine Learning.",
            properties={},
        )
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        RelationshipExtractionResponse(
            relationships=expected_relationships
        )
    )

    extractor = RelationshipExtractor(mock_gemini)
    relationships = extractor.extract(sample_chunk, entities)

    assert len(relationships) == 1
    assert relationships[0].source_entity_name == "Python"
    assert relationships[0].target_entity_name == "Machine Learning"


def test_unknown_relationship_entities_filtered(
    sample_chunk,
    mock_gemini,
):
    """Test relationships with unknown entities are discarded."""

    entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
        ),
        ExtractedEntity(
            name="Machine Learning",
            entity_type="AI Concept",
        ),
    ]

    expected_relationships = [
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Machine Learning",
            relation_type="USED_FOR",
        ),
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Unknown",
            relation_type="RELATED_TO",
        ),
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        RelationshipExtractionResponse(
            relationships=expected_relationships
        )
    )

    extractor = RelationshipExtractor(mock_gemini)
    relationships = extractor.extract(sample_chunk, entities)

    assert len(relationships) == 1
    assert relationships[0].target_entity_name == "Machine Learning"


def test_no_entities_means_no_relationship_api_call(
    sample_chunk,
    mock_gemini,
):
    """Test relationship extraction is skipped without entities."""

    extractor = RelationshipExtractor(mock_gemini)

    relationships = extractor.extract(sample_chunk, [])

    assert relationships == []

    mock_gemini._model.with_structured_output.assert_not_called()


def test_relationship_deduplication(
    sample_chunk,
    mock_gemini,
):
    """Test duplicate relationships are removed."""

    entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
        ),
        ExtractedEntity(
            name="Machine Learning",
            entity_type="AI Concept",
        ),
    ]

    duplicate_relationships = [
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Machine Learning",
            relation_type="USED_FOR",
        ),
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Machine Learning",
            relation_type="used_for",
            description="Duplicate.",
        ),
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.return_value = (
        RelationshipExtractionResponse(
            relationships=duplicate_relationships
        )
    )

    extractor = RelationshipExtractor(mock_gemini)
    relationships = extractor.extract(sample_chunk, entities)

    assert len(relationships) == 1


def test_invalid_relationship_json(
    sample_chunk,
    mock_gemini,
):
    """Test invalid structured relationship response handling."""

    entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
        )
    ]

    mock_gemini._model.with_structured_output.return_value.invoke.side_effect = (
        ValueError("invalid JSON")
    )

    extractor = RelationshipExtractor(mock_gemini)

    with pytest.raises(
        RuntimeError,
        match="Relationship extraction failed",
    ):
        extractor.extract(sample_chunk, entities)


# ============================================================
# EXTRACTION SERVICE TESTS
# ============================================================

def test_extraction_service(sample_chunk):
    """Test the complete extraction service."""

    entity_extractor = MagicMock()
    relationship_extractor = MagicMock()

    entities = [
        ExtractedEntity(
            name="Python",
            entity_type="Programming Language",
        )
    ]

    relationships = [
        ExtractedRelationship(
            source_entity_name="Python",
            target_entity_name="Machine Learning",
            relation_type="USED_FOR",
        )
    ]

    entity_extractor.extract.return_value = entities
    relationship_extractor.extract.return_value = relationships

    service = ExtractionService(
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
    )

    result = service.extract(sample_chunk)

    assert result.document_id == sample_chunk.document_id
    assert result.chunk_id == sample_chunk.chunk_id
    assert result.entities == entities
    assert result.relationships == relationships

    entity_extractor.extract.assert_called_once_with(sample_chunk)

    relationship_extractor.extract.assert_called_once_with(
        sample_chunk,
        entities,
    )


def test_extraction_service_rejects_empty_chunk(sample_chunk):
    """Test that empty chunks are rejected."""

    sample_chunk.text = "   "

    entity_extractor = MagicMock()
    relationship_extractor = MagicMock()

    service = ExtractionService(
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
    )

    with pytest.raises(ValueError, match="empty chunk"):
        service.extract(sample_chunk)

    entity_extractor.extract.assert_not_called()
    relationship_extractor.extract.assert_not_called()
