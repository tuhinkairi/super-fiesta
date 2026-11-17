from pydantic import BaseModel, ConfigDict, Field

from modules.artist_graph_rag.src.graphrag_app.chunking.models import DocumentChunk
from modules.artist_graph_rag.src.graphrag_app.extraction.gemini_client import (
    GeminiClient,
)
from modules.artist_graph_rag.src.graphrag_app.extraction.models import ExtractedEntity


class EntityExtractionResponse(BaseModel):
    """Structured response containing extracted entities."""

    model_config = ConfigDict(extra="forbid")

    entities: list[ExtractedEntity] = Field(default_factory=list)


class EntityExtractor:
    """Extracts meaningful entities using LangChain and Gemini."""

    SYSTEM_INSTRUCTION = """
    You are an expert knowledge graph entity extraction system.

    Extract meaningful entities explicitly present in the
    supplied document chunk.

    Rules:
    1. Extract only entities supported by the text.
    2. Never invent entities or facts.
    3. Use consistent entity types.
    4. Provide concise and factual descriptions.
    5. Include useful properties when available.
    6. Avoid duplicate entities.
    7. Return only entities relevant to the knowledge graph.
    """

    def __init__(
        self,
        gemini_client: GeminiClient | None = None,
    ):
        self.gemini_client = gemini_client or GeminiClient()

    def extract(
        self,
        chunk: DocumentChunk,
    ) -> list[ExtractedEntity]:
        """Extract and validate entities from a document chunk."""

        if not chunk.text or not chunk.text.strip():
            raise ValueError("Chunk text cannot be empty.")

        prompt = f"""
        Extract all meaningful entities from the following
        document chunk.

        Document ID: {chunk.document_id}
        Chunk ID: {chunk.chunk_id}

        Document text:
        {chunk.text}
        """

        try:
            structured_model = self.gemini_client._model.with_structured_output(
                EntityExtractionResponse,
                method="json_schema",
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
                f"Entity extraction failed for chunk " f"{chunk.chunk_id}: {error}"
            ) from error

        if not isinstance(response, EntityExtractionResponse):
            raise RuntimeError("Gemini returned an unexpected entity response format.")

        unique_entities = {}

        for entity in response.entities:
            normalized_name = entity.name.strip().casefold()
            normalized_type = entity.entity_type.strip().casefold()

            if not normalized_name or not normalized_type:
                continue

            identity = (normalized_name, normalized_type)

            if identity not in unique_entities:
                unique_entities[identity] = entity

        return list(unique_entities.values())
