from graphrag_app.chunking.models import DocumentChunk

from graphrag_app.extraction.models import ChunkExtractionResult
from graphrag_app.extraction.entity_extractor import EntityExtractor
from graphrag_app.extraction.relationship_extractor import (
    RelationshipExtractor,
)


class ExtractionService:
    """Coordinates entity and relationship extraction."""

    def __init__(
        self,
        entity_extractor: EntityExtractor | None = None,
        relationship_extractor: RelationshipExtractor | None = None,
    ):
        self.entity_extractor = (
            entity_extractor or EntityExtractor()
        )

        self.relationship_extractor = (
            relationship_extractor or RelationshipExtractor()
        )

    def extract(
        self,
        chunk: DocumentChunk,
    ) -> ChunkExtractionResult:
        """Extract entities and relationships from one chunk."""

        if not chunk.text.strip():
            raise ValueError(
                "Cannot extract knowledge from an empty chunk."
            )

        # Step 1: Extract entities.
        entities = self.entity_extractor.extract(chunk)

        # Step 2: Extract relationships between those entities.
        relationships = self.relationship_extractor.extract(
            chunk,
            entities,
        )

        # Step 3: Combine both extraction results.
        return ChunkExtractionResult(
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            entities=entities,
            relationships=relationships,
        )
