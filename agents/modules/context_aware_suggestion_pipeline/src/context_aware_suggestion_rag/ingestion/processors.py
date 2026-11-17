"""
Document processing pipeline.

Coordinates document loading, text extraction, and chunking
to prepare documents for embedding and vector storage.
"""

from pathlib import Path
from time import perf_counter

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.identifiers import generate_document_id
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import ProcessingStatus
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import (
    ContextAwareSuggestionError,
    DocumentLoadError,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.chunkers import (
    ChunkingConfig,
    DocumentChunker,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.loaders import DocumentLoader
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.models import (
    ExtractionResult,
    IngestionResult,
)


class DocumentProcessor:
    """Processes documents into extracted text and chunks."""

    def __init__(
        self,
        loader: DocumentLoader | None = None,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self.loader = loader or DocumentLoader()
        self.chunker = chunker or DocumentChunker()

    def process(
        self,
        file_path: str | Path,
        document_id: str | None = None,
    ) -> tuple[IngestionResult, list]:
        """
        Load and chunk a document.

        Args:
            file_path: Path to the source document.
            document_id: Optional existing document identifier.

        Returns:
            A tuple containing the ingestion result and generated chunks.

        Raises:
            DocumentLoadError: If document extraction fails.
            ChunkingError: If document chunking fails.
        """

        start_time = perf_counter()
        document_id = document_id or generate_document_id()

        try:
            extraction: ExtractionResult = self.loader.load(file_path)

            chunks = self.chunker.chunk_text(
                text=extraction.extracted_text,
                document_id=document_id,
            )

            result = IngestionResult(
                document_id=document_id,
                filename=extraction.filename,
                document_type=extraction.document_type,
                status=ProcessingStatus.PROCESSED,
                extracted_text=extraction.extracted_text,
                total_pages=extraction.total_pages,
                total_characters=extraction.total_characters,
                file_size_bytes=Path(file_path).stat().st_size,
                warnings=extraction.warnings,
                completed_at=extraction.extracted_at,
            )

            return result, chunks

        except ContextAwareSuggestionError:
            raise

        except Exception as exc:
            raise DocumentLoadError(
                f"Document processing failed: {exc}"
            ) from exc

        finally:
            _ = perf_counter() - start_time


def process_document(
    file_path: str | Path,
    document_id: str | None = None,
    chunking_config: ChunkingConfig | None = None,
) -> tuple[IngestionResult, list]:
    """Convenience function for processing a document."""

    processor = DocumentProcessor(
        chunker=DocumentChunker(chunking_config)
    )

    return processor.process(
        file_path=file_path,
        document_id=document_id,
    )


__all__ = [
    "DocumentProcessor",
    "process_document",
]
