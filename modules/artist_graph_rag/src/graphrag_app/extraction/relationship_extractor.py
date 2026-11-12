
from pydantic import BaseModel, ConfigDict, Field

from graphrag_app.chunking.models import DocumentChunk
from graphrag_app.extraction.gemini_client import GeminiClient
from graphrag_app.extraction.models import (
    ExtractedEntity,
    ExtractedRelationship,
)


class RelationshipExtractionResponse(BaseModel):
    """Structured response containing extracted relationships."""

    model_config = ConfigDict(extra="forbid")

    relationships: list[ExtractedRelationship] = Field(
        default_factory=list
    )


class RelationshipExtractor:
    """Extracts relationships using LangChain and Gemini."""

    SYSTEM_INSTRUCTION = """
    You are an expert knowledge graph relationship extraction system.

    Identify meaningful relationships between the supplied entities
    using only the information explicitly available in the document.

    Rules:
    1. Only use entities supplied in the entity list.
    2. Never invent entities or relationships.
    3. Preserve the exact entity names provided.
    4. Use concise, meaningful relationship types.
    5. Use uppercase snake_case for relationship types.
    6. Provide factual descriptions.
    7. Avoid duplicate relationships.
    8. Return only relationships supported by the text.
    """

    def __init__(
        self,
        gemini_client: GeminiClient | None = None,
    ):
        self.gemini_client = gemini_client or GeminiClient()

    def extract(
        self,
        chunk: DocumentChunk,
        entities: list[ExtractedEntity],
    ) -> list[ExtractedRelationship]:
        """Extract relationships between known entities."""

        if not chunk.text or not chunk.text.strip():
            raise ValueError("Chunk text cannot be empty.")

        if not entities:
            return []

        entity_names = [
            entity.name.strip()
            for entity in entities
        ]

        prompt = f"""
        Extract meaningful relationships from the following
        document chunk.

        Document ID: {chunk.document_id}
        Chunk ID: {chunk.chunk_id}

        Available entities:
        {entity_names}

        Document text:
        {chunk.text}

        Extract relationships only between the available entities.
        Do not introduce new entity names.
        """

        try:
            structured_model = (
                self.gemini_client._model.with_structured_output(
                    RelationshipExtractionResponse,
                    method="json_schema",
                )
            )

            response = structured_model.invoke(
                [
                    (
                        "system",
                        self.SYSTEM_INSTRUCTION,
                    ),
                    (
                        "human",
                        prompt,
                    ),
                ]
            )

        except Exception as error:
            raise RuntimeError(
                f"Relationship extraction failed for chunk "
                f"{chunk.chunk_id}: {error}"
            ) from error

        if not isinstance(response, RelationshipExtractionResponse):
            raise RuntimeError(
                "Gemini returned an unexpected relationship response format."
            )

        valid_entity_names = {
            name.casefold()
            for name in entity_names
        }

        valid_relationships = []

        for relationship in response.relationships:
            source_name = relationship.source_entity_name.strip()
            target_name = relationship.target_entity_name.strip()

            if (
                source_name.casefold() not in valid_entity_names
                or target_name.casefold() not in valid_entity_names
            ):
                continue

            valid_relationships.append(
                relationship.model_copy(
                    update={
                        "source_entity_name": source_name,
                        "target_entity_name": target_name,
                        "relation_type": relationship.relation_type.strip().upper(),
                    }
                )
            )

        return self._remove_duplicates(valid_relationships)

    @staticmethod
    def _remove_duplicates(
        relationships: list[ExtractedRelationship],
    ) -> list[ExtractedRelationship]:
        """Remove duplicate relationships while preserving order."""

        unique_relationships = {}
        
        for relationship in relationships:
            identity = (
                relationship.source_entity_name.casefold(),
                relationship.target_entity_name.casefold(),
                relationship.relation_type.casefold(),
            )

            if identity not in unique_relationships:
                unique_relationships[identity] = relationship

        return list(unique_relationships.values())
