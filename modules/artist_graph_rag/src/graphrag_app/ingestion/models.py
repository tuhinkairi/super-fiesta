from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class IngestionStatus(str, Enum):
    """Possible states of document ingestion."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionRequest(BaseModel):
    """Represents a request to ingest an uploaded document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    filename: str = Field(min_length=1)
    file_path: str = Field(min_length=1)

    content_type: str | None = None



class IngestionResult(BaseModel):
    """Represents the result of document ingestion."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)

    status: IngestionStatus = IngestionStatus.PENDING

    message: str | None = None
    stored_path: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    processed_at: datetime | None = None
    error: str | None = None
