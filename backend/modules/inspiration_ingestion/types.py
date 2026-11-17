
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


InspirationType = Literal["pdf", "image", "text", "url"]


class InspirationRecord(BaseModel):
    """
    Represents one piece of inspiration stored in the workspace.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    # Unique identifier for each inspiration item.
    id: str = Field(default_factory=lambda: str(uuid4()))

    # Original file information.
    file_name: str
    content_type: InspirationType
    source: str | None = None
    storage_path: str | None = None

    # Upload information.
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Extracted content.
    extracted_text: str = ""

    # AI-generated information.
    summary: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    mood_tags: list[str] = Field(default_factory=list)

    # Original source and processing information.
    provenance: dict[str, Any] = Field(default_factory=dict)

    # Vector representation for semantic search.
    embedding: list[float] | None = None
