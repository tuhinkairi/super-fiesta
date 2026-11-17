"""
Batch document ingestion.

Processes multiple documents and collects their individual
ingestion results into a single batch report.
"""

from pathlib import Path
from time import perf_counter

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.identifiers import generate_id
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import ProcessingStatus
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import ContextAwareSuggestionError
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.chunkers import (
    ChunkingConfig,
    DocumentChunker,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.loaders import DocumentLoader
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.models import (
    IngestionBatch,
    IngestionResult,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.processors import DocumentProcessor
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.types import DocumentChunk


class BatchDocumentProcessor:
    """Processes multiple documents and aggregates their results."""

    def __init__(
        self,
        processor: DocumentProcessor | None = None,
    ) -> None:
        self.processor = processor or DocumentProcessor()

    def process(
        self,
        file_paths: list[str | Path],
    ) -> tuple[IngestionBatch, list[DocumentChunk]]:
        """
        Process a collection of document paths.

        Individual document failures are recorded without stopping
        the processing of other documents.

        Args:
            file_paths: Paths of documents to process.

        Returns:
            The batch summary and all successfully generated chunks.
        """

        start_time = perf_counter()

        batch = IngestionBatch(
            batch_id=generate_id("batch"),
            total_documents=len(file_paths),
        )

        all_chunks: list[DocumentChunk] = []

        for file_path in file_paths:
            try:
                result, chunks = self.processor.process(file_path)

                batch.results.append(result)
                all_chunks.extend(chunks)

            except ContextAwareSuggestionError as exc:
                path = Path(file_path)

                batch.results.append(
                    IngestionResult(
                        document_id=generate_id("doc"),
                        filename=path.name,
                        document_type=self._get_document_type(path),
                        status=ProcessingStatus.FAILED,
                        error_message=str(exc),
                    )
                )

            except Exception as exc:
                path = Path(file_path)

                batch.results.append(
                    IngestionResult(
                        document_id=generate_id("doc"),
                        filename=path.name,
                        document_type=self._get_document_type(path),
                        status=ProcessingStatus.FAILED,
                        error_message=f"Unexpected error: {exc}",
                    )
                )

        batch.successful_documents = sum(
            result.status == ProcessingStatus.PROCESSED
            for result in batch.results
        )

        batch.failed_documents = sum(
            result.status == ProcessingStatus.FAILED
            for result in batch.results
        )

        batch.validate_counts()

        _ = perf_counter() - start_time

        return batch, all_chunks

    @staticmethod
    def _get_document_type(path: Path):
        """Determine document type from its extension."""

        from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import DocumentType

        try:
            return DocumentType(path.suffix.lower().lstrip("."))
        except ValueError:
            return DocumentType.TXT


def process_documents(
    file_paths: list[str | Path],
    chunking_config: ChunkingConfig | None = None,
) -> tuple[IngestionBatch, list[DocumentChunk]]:
    """Convenience function for batch document processing."""

    processor = DocumentProcessor(
        loader=DocumentLoader(),
        chunker=DocumentChunker(chunking_config),
    )

    batch_processor = BatchDocumentProcessor(processor)

    return batch_processor.process(file_paths)


__all__ = [
    "BatchDocumentProcessor",
    "process_documents",
]
