
"""Tests for document ingestion and context integration."""

from pathlib import Path

from context_aware_suggestion_rag.document_context import (
    DocumentContextProcessor,
)
from context_aware_suggestion_rag.exceptions import ContextExtractionError
from context_aware_suggestion_rag.ingestion.models import IngestionResult
from context_aware_suggestion_rag.domain.enums import (
    DocumentType,
    ProcessingStatus,
)


class FakeIngestionService:
    def __init__(self, extracted_text="Artificial intelligence and RAG systems."):
        self.extracted_text = extracted_text
        self.received_path = None
        self.received_document_id = None

    def ingest_document(self, file_path, document_id=None):
        self.received_path = file_path
        self.received_document_id = document_id

        result = IngestionResult(
            document_id=document_id or "doc_test_001",
            filename="research.txt",
            document_type=DocumentType.TXT,
            status=ProcessingStatus.PROCESSED,
            extracted_text=self.extracted_text,
            total_characters=len(self.extracted_text),
        )

        return result, []


class FakeContextService:
    def __init__(self):
        self.received_arguments = None

    def process_document(self, **kwargs):
        self.received_arguments = kwargs
        return object(), object()


def test_document_ingestion_and_context_processing():
    ingestion = FakeIngestionService()
    context = FakeContextService()

    processor = DocumentContextProcessor(
        ingestion_service=ingestion,
        context_service=context,
    )

    result = processor.process_document(
        file_path="research.txt",
        document_id="doc_test_001",
    )

    assert result.ingestion_result.document_id == "doc_test_001"
    assert result.ingestion_result.extracted_text
    assert result.context is not None
    assert result.analysis is not None

    assert context.received_arguments["text"] == ingestion.extracted_text
    assert context.received_arguments["document_id"] == "doc_test_001"
    assert context.received_arguments["title"] == "research.txt"


def test_language_and_region_are_forwarded():
    ingestion = FakeIngestionService()
    context = FakeContextService()

    processor = DocumentContextProcessor(
        ingestion_service=ingestion,
        context_service=context,
    )

    processor.process_document(
        file_path=Path("research.txt"),
        language="en",
        region="IN",
        generate_summary=False,
    )

    arguments = context.received_arguments

    assert arguments["language"] == "en"
    assert arguments["region"] == "IN"
    assert arguments["generate_summary"] is False


def test_empty_extracted_text_is_rejected():
    ingestion = FakeIngestionService(extracted_text="")
    context = FakeContextService()

    processor = DocumentContextProcessor(
        ingestion_service=ingestion,
        context_service=context,
    )

    try:
        processor.process_document("empty.txt")
    except ContextExtractionError:
        pass
    else:
        raise AssertionError("Expected ContextExtractionError")

    assert context.received_arguments is None


def test_document_id_is_preserved():
    ingestion = FakeIngestionService()
    context = FakeContextService()

    processor = DocumentContextProcessor(
        ingestion_service=ingestion,
        context_service=context,
    )

    result = processor.process_document(
        "research.txt",
        document_id="custom_document_123",
    )

    assert result.ingestion_result.document_id == "custom_document_123"
    assert context.received_arguments["document_id"] == "custom_document_123"


if __name__ == "__main__":
    tests = [
        test_document_ingestion_and_context_processing,
        test_language_and_region_are_forwarded,
        test_empty_extracted_text_is_rejected,
        test_document_id_is_preserved,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("\nAll document-context integration tests passed.")
