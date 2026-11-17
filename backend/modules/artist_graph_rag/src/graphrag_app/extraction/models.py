from pydantic import BaseModel, ConfigDict, Field


class ExtractedEntity(BaseModel):
    """Represents an entity identified in a document chunk."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)

    description: str | None = None

    properties: dict[
        str,
        str | int | float | bool
    ] = Field(default_factory=dict)


class ExtractedRelationship(BaseModel):
    """Represents a relationship identified between entities."""

    model_config = ConfigDict(extra="forbid")

    source_entity_name: str = Field(min_length=1)
    target_entity_name: str = Field(min_length=1)

    relation_type: str = Field(min_length=1)

    description: str | None = None

    properties: dict[
        str,
        str | int | float | bool
    ] = Field(default_factory=dict)


class ChunkExtractionResult(BaseModel):
    """Contains entities and relationships extracted from one chunk."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)

    entities: list[ExtractedEntity] = Field(
        default_factory=list
    )

    relationships: list[ExtractedRelationship] = Field(
        default_factory=list
    )
