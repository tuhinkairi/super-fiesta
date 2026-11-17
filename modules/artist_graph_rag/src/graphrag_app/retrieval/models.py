from pydantic import BaseModel, ConfigDict, Field


class RetrievalRequest(BaseModel):
    """Represents a request to retrieve relevant knowledge."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)

    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    document_id: str | None = None


class RetrievedEntity(BaseModel):
    """Represents an entity retrieved from the knowledge graph."""

    model_config = ConfigDict(extra="forbid")

    entity_id: str = Field(min_length=1)

    name: str = Field(min_length=1)

    entity_type: str = Field(min_length=1)

    description: str | None = None

    properties: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )

    source_document_id: str | None = None

    source_chunk_id: str | None = None

    relevance_score: float | None = None


class RetrievalResult(BaseModel):
    """Contains the complete result of a retrieval operation."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)

    entities: list[RetrievedEntity] = Field(
        default_factory=list
    )

    relationships: list[dict[str, str | None]] = Field(
        default_factory=list
    )

    context: str = ""

    total_entities: int = Field(default=0, ge=0)

    total_relationships: int = Field(default=0, ge=0)
