"""
Local ingestion storage.

Persists ingestion results and document chunks as JSON files.
This storage layer is independent of Pinecone.
"""

from pathlib import Path
from typing import Any

from context_aware_suggestion_rag.core.identifiers import (
    generate_id,
)
from context_aware_suggestion_rag.core.paths import ensure_directory
from context_aware_suggestion_rag.core.serialization import (
    load_json_file,
    save_json_file,
)
from context_aware_suggestion_rag.domain.entities import DocumentChunkEntity
from context_aware_suggestion_rag.exceptions import (
    ContextAwareSuggestionError,
)
from context_aware_suggestion_rag.ingestion.models import IngestionResult


class IngestionStorageError(ContextAwareSuggestionError):
    """Raised when local ingestion storage operations fail."""


class IngestionStorage:
    """Stores and retrieves ingestion data using JSON files."""

    def __init__(
        self,
        storage_directory: str | Path = "data/ingestion",
    ) -> None:
        self.storage_directory = ensure_directory(storage_directory)

        self.documents_directory = ensure_directory(
            self.storage_directory / "documents"
        )

        self.chunks_directory = ensure_directory(
            self.storage_directory / "chunks"
        )

    def save_document(
        self,
        result: IngestionResult,
    ) -> Path:
        """Save an ingestion result."""

        try:
            file_path = self.documents_directory / (
                f"{result.document_id}.json"
            )

            save_json_file(
                result.model_dump(mode="json"),
                file_path,
            )

            return file_path

        except Exception as exc:
            raise IngestionStorageError(
                f"Failed to save document '{result.document_id}': {exc}"
            ) from exc

    def get_document(
        self,
        document_id: str,
    ) -> IngestionResult | None:
        """Retrieve an ingestion result by document ID."""

        file_path = self.documents_directory / f"{document_id}.json"

        if not file_path.is_file():
            return None

        try:
            data = load_json_file(file_path)
            return IngestionResult.model_validate(data)

        except Exception as exc:
            raise IngestionStorageError(
                f"Failed to retrieve document '{document_id}': {exc}"
            ) from exc

    def save_chunks(
        self,
        document_id: str,
        chunks: list[DocumentChunkEntity],
    ) -> Path:
        """Save all chunks belonging to a document."""

        try:
            file_path = self.chunks_directory / f"{document_id}.json"

            chunk_data = [
                chunk.model_dump(mode="json")
                for chunk in chunks
            ]

            save_json_file(
                {
                    "document_id": document_id,
                    "total_chunks": len(chunks),
                    "chunks": chunk_data,
                },
                file_path,
            )

            return file_path

        except Exception as exc:
            raise IngestionStorageError(
                f"Failed to save chunks for '{document_id}': {exc}"
            ) from exc

    def get_chunks(
        self,
        document_id: str,
    ) -> list[DocumentChunkEntity]:
        """Retrieve all chunks belonging to a document."""

        file_path = self.chunks_directory / f"{document_id}.json"

        if not file_path.is_file():
            return []

        try:
            data: dict[str, Any] = load_json_file(file_path)

            return [
                DocumentChunkEntity.model_validate(item)
                for item in data.get("chunks", [])
            ]

        except Exception as exc:
            raise IngestionStorageError(
                f"Failed to retrieve chunks for '{document_id}': {exc}"
            ) from exc

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        """Delete stored document data and its chunks."""

        document_path = self.documents_directory / f"{document_id}.json"
        chunks_path = self.chunks_directory / f"{document_id}.json"

        deleted = False

        try:
            for file_path in (document_path, chunks_path):
                if file_path.is_file():
                    file_path.unlink()
                    deleted = True

            return deleted

        except OSError as exc:
            raise IngestionStorageError(
                f"Failed to delete document '{document_id}': {exc}"
            ) from exc

    def list_documents(self) -> list[str]:
        """Return IDs of all locally stored documents."""

        return sorted(
            file_path.stem
            for file_path in self.documents_directory.glob("*.json")
        )


__all__ = [
    "IngestionStorageError",
    "IngestionStorage",
]
