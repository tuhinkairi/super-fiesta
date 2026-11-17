from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DocumentChunk(BaseModel):
    """Represents a chunk extracted from a document."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    document_id: str = Field(min_length=1)

    chunk_index: int = Field(ge=0)

    text: str = Field(min_length=1)

    start_char: int = Field(ge=0)

    end_char: int = Field(ge=1)

    character_count: int = Field(ge=1)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
