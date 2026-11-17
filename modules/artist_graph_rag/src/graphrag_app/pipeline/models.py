
from datetime import datetime, timezone
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class PipelineStatus(str, Enum):
    """Possible states of document processing."""

    COMPLETED = "completed"
    FAILED = "failed"


class DocumentPipelineResult(BaseModel):
    """Represents the outcome of the document-to-graph pipeline."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)

    status: PipelineStatus

    chunks_created: int = Field(default=0, ge=0)
    entities_stored: int = Field(default=0, ge=0)
    relationships_stored: int = Field(default=0, ge=0)

    message: str | None = None
    error: str | None = None

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("document_id", "filename")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value

    @field_validator("message", "error")
    @classmethod
    def normalize_optional_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @property
    def success(self) -> bool:
        """Return whether document processing completed successfully."""

        return self.status == PipelineStatus.COMPLETED
