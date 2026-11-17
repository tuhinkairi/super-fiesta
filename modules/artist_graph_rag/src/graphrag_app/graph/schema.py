from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel):
    """Represents an entity extracted from a document."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)

    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    source_document_id: str | None = None
    source_chunk_id: str | None = None


class Relationship(BaseModel):
    """Represents a relationship between two entities."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))

    source_entity_id: str = Field(min_length=1)
    target_entity_id: str = Field(min_length=1)

    relation_type: str = Field(min_length=1)

    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    source_document_id: str | None = None
    source_chunk_id: str | None = None
