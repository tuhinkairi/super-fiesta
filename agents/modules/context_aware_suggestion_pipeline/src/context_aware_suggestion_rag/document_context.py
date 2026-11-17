"""Integration between document ingestion and context processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.analyzers import ContextAnalysis
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import ExtractedContext
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.service import ContextService
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import DocumentChunkEntity
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import ContextExtractionError
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.models import IngestionResult
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.service import (
    DocumentIngestionService,
)


@dataclass(slots=True)
class DocumentContextResult:
    """Combined result of document ingestion and context processing."""

    ingestion_result: IngestionResult
    chunks: list[DocumentChunkEntity]
    context: ExtractedContext
    analysis: ContextAnalysis


class DocumentContextProcessor:
    """Connect document ingestion with context extraction and analysis."""

    def __init__(
        self,
        ingestion_service: DocumentIngestionService | None = None,
        context_service: ContextService | None = None,
    ) -> None:
        self.ingestion_service = (
            ingestion_service
            if ingestion_service is not None
            else DocumentIngestionService()
        )

        self.context_service = (
            context_service
            if context_service is not None
            else ContextService()
        )

    def process_document(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        language: str = "en",
        region: str = "IN",
        generate_summary: bool = True,
    ) -> DocumentContextResult:
        """Ingest a document and process its extracted contextual data."""

        ingestion_result, chunks = self.ingestion_service.ingest_document(
            file_path=file_path,
            document_id=document_id,
        )

        extracted_text = ingestion_result.extracted_text

        if not extracted_text or not extracted_text.strip():
            raise ContextExtractionError(
                "Cannot extract context because the document contains no text."
            )

        context, analysis = self.context_service.process_document(
            text=extracted_text,
            document_id=ingestion_result.document_id,
            title=ingestion_result.filename,
            language=language,
            region=region,
            generate_summary=generate_summary,
        )

        return DocumentContextResult(
            ingestion_result=ingestion_result,
            chunks=chunks,
            context=context,
            analysis=analysis,
        )


__all__ = [
    "DocumentContextResult",
    "DocumentContextProcessor",
]
