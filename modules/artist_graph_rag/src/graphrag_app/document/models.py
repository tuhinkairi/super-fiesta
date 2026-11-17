
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ExtractedDocument(BaseModel):
    """Represents the text extracted from an uploaded document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)

    extraction_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    filename: str = Field(min_length=1)

    text: str = Field(min_length=1)

    page_count: int | None = Field(
        default=None,
        ge=1,
    )

    character_count: int = Field(ge=0)

    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
