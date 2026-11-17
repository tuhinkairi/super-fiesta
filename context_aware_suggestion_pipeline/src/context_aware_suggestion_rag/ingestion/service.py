"""
Document ingestion service.

Coordinates document validation, extraction, chunking,
and local persistence for single and batch ingestion.
"""

from pathlib import Path

from context_aware_suggestion_rag.core.identifiers import generate_document_id
from context_aware_suggestion_rag.domain.entities import DocumentChunkEntity
from context_aware_suggestion_rag.exceptions import ContextAwareSuggestionError
from context_aware_suggestion_rag.ingestion.batch import (
    BatchDocumentProcessor,
)
from context_aware_suggestion_rag.ingestion.chunkers import (
    ChunkingConfig,
    DocumentChunker,
)
from context_aware_suggestion_rag.ingestion.loaders import DocumentLoader
from context_aware_suggestion_rag.ingestion.models import (
    IngestionBatch,
    IngestionResult,
)
from context_aware_suggestion_rag.ingestion.processors import (
    DocumentProcessor,
)
from context_aware_suggestion_rag.ingestion.storage import (
    IngestionStorage,
)


class DocumentIngestionService:
    """Provides document ingestion operations."""

    def __init__(
        self,
        storage: IngestionStorage | None = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> None:
        self.storage = storage or IngestionStorage()

        self.loader = DocumentLoader()

        self.chunker = DocumentChunker(
            config=chunking_config,
        )

        self.processor = DocumentProcessor(
            loader=self.loader,
            chunker=self.chunker,
        )

        self.batch_processor = BatchDocumentProcessor(
            processor=self.processor,
        )

    def ingest_document(
        self,
        file_path: str | Path,
        document_id: str | None = None,
    ) -> tuple[IngestionResult, list[DocumentChunkEntity]]:
        """
        Ingest a single document and persist its result and chunks.

        Returns:
            A tuple containing the ingestion result and chunks.
        """

        document_id = document_id or generate_document_id()

        try:
            result, chunks = self.processor.process(
                file_path=file_path,
                document_id=document_id,
            )

            self.storage.save_document(result)
            self.storage.save_chunks(document_id, chunks)

            return result, chunks

        except ContextAwareSuggestionError:
            raise

        except Exception as exc:
            raise ContextAwareSuggestionError(
                f"Document ingestion failed: {exc}"
            ) from exc

    def ingest_documents(
        self,
        file_paths: list[str | Path],
    ) -> tuple[IngestionBatch, list[DocumentChunkEntity]]:
        """
        Ingest multiple documents and persist successful results.

        Failed documents remain recorded in the batch report.
        """

        try:
            batch, chunks = self.batch_processor.process(file_paths)

            for result in batch.results:
                self.storage.save_document(result)

            chunks_by_document: dict[str, list[DocumentChunkEntity]] = {}

            for chunk in chunks:
                chunks_by_document.setdefault(
                    chunk.document_id,
                    [],
                ).append(chunk)

            for document_id, document_chunks in chunks_by_document.items():
                self.storage.save_chunks(
                    document_id,
                    document_chunks,
                )

            return batch, chunks

        except ContextAwareSuggestionError:
            raise

        except Exception as exc:
            raise ContextAwareSuggestionError(
                f"Batch ingestion failed: {exc}"
            ) from exc

    def get_document(
        self,
        document_id: str,
    ) -> IngestionResult | None:
        """Retrieve a previously ingested document."""

        return self.storage.get_document(document_id)

    def get_document_chunks(
        self,
        document_id: str,
    ) -> list[DocumentChunkEntity]:
        """Retrieve chunks belonging to a document."""

        return self.storage.get_chunks(document_id)

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        """Delete locally stored ingestion data."""

        return self.storage.delete_document(document_id)


__all__ = [
    "DocumentIngestionService",
]
