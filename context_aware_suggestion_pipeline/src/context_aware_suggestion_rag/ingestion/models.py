"""
Ingestion models.

Defines structured data models used during document loading,
text extraction, and ingestion processing.
"""

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from context_aware_suggestion_rag.domain.enums import (
    DocumentType,
    ProcessingStatus,
)


def current_utc_time() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class IngestionModel(BaseModel):
    """Base model for ingestion-specific structures."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class DocumentSource(IngestionModel):
    """Represents the original source of an uploaded document."""

    filename: str = Field(min_length=1, max_length=255)
    file_path: Path | None = None
    document_type: DocumentType
    file_size_bytes: int = Field(ge=0)
    source_name: str | None = None


class ExtractionResult(IngestionModel):
    """Represents the result of extracting text from a document."""

    filename: str = Field(min_length=1)
    document_type: DocumentType
    extracted_text: str
    total_pages: int | None = Field(default=None, ge=1)
    total_characters: int = Field(ge=0)
    extraction_time_seconds: float = Field(default=0.0, ge=0)
    warnings: list[str] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=current_utc_time)


class IngestionResult(IngestionModel):
    """Represents the complete result of document ingestion."""

    document_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    document_type: DocumentType
    status: ProcessingStatus = ProcessingStatus.PENDING
    extracted_text: str = ""
    total_pages: int | None = Field(default=None, ge=1)
    total_characters: int = Field(default=0, ge=0)
    file_size_bytes: int = Field(default=0, ge=0)
    warnings: list[str] = Field(default_factory=list)
    error_message: str | None = None
    created_at: datetime = Field(default_factory=current_utc_time)
    completed_at: datetime | None = None


class IngestionBatch(IngestionModel):
    """Represents a batch of document ingestion results."""

    batch_id: str = Field(min_length=1)
    results: list[IngestionResult] = Field(default_factory=list)
    total_documents: int = Field(default=0, ge=0)
    successful_documents: int = Field(default=0, ge=0)
    failed_documents: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=current_utc_time)

    def validate_counts(self) -> None:
        """Ensure batch counters match the stored results."""

        if self.total_documents != len(self.results):
            raise ValueError(
                "total_documents does not match the number of results."
            )

        successful = sum(
            result.status == ProcessingStatus.PROCESSED
            for result in self.results
        )

        failed = sum(
            result.status == ProcessingStatus.FAILED
            for result in self.results
        )

        if self.successful_documents != successful:
            raise ValueError(
                "successful_documents does not match the results."
            )

        if self.failed_documents != failed:
            raise ValueError(
                "failed_documents does not match the results."
            )


__all__ = [
    "IngestionModel",
    "DocumentSource",
    "ExtractionResult",
    "IngestionResult",
    "IngestionBatch",
    "current_utc_time",
]
