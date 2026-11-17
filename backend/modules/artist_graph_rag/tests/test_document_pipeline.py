from unittest.mock import MagicMock

from graphrag_app.ingestion import (
    IngestionRequest,
    IngestionResult,
    IngestionStatus,
)

from graphrag_app.pipeline.models import PipelineStatus

from graphrag_app.pipeline.document_pipeline import (
    DocumentPipeline,
)


def create_pipeline():
    """Create a pipeline with mocked dependencies."""

    ingestion_service = MagicMock()
    document_service = MagicMock()
    chunking_service = MagicMock()
    extraction_service = MagicMock()
    graph_ingestion_service = MagicMock()

    pipeline = DocumentPipeline(
        ingestion_service=ingestion_service,
        document_service=document_service,
        chunking_service=chunking_service,
        extraction_service=extraction_service,
        graph_ingestion_service=graph_ingestion_service,
    )

    return (
        pipeline,
        ingestion_service,
        document_service,
        chunking_service,
        extraction_service,
        graph_ingestion_service,
    )


def create_request():
    """Create a sample document ingestion request."""

    return IngestionRequest(
        document_id="document-001",
        filename="machine_learning.txt",
        file_path="sample.txt",
    )


def test_successful_document_pipeline():
    """Test the complete document-to-graph workflow."""

    (
        pipeline,
        ingestion_service,
        document_service,
        chunking_service,
        extraction_service,
        graph_ingestion_service,
    ) = create_pipeline()

    request = create_request()

    # Mock successful document ingestion.
    ingestion_service.ingest.return_value = IngestionResult(
        document_id=request.document_id,
        status=IngestionStatus.COMPLETED,
        stored_path="data/uploads/machine_learning.txt",
    )

    # Mock document extraction.
    extracted_document = MagicMock()

    document_service.process.return_value = extracted_document

    # Mock chunking.
    chunks = [
        MagicMock(),
        MagicMock(),
    ]

    chunking_service.chunk_document.return_value = chunks

    # Mock Gemini extraction.
    extraction_service.extract.return_value = MagicMock()

    # Mock graph storage for each chunk.
    graph_ingestion_service.store_extraction.side_effect = [
        {
            "entities_stored": 5,
            "relationships_stored": 3,
        },
        {
            "entities_stored": 4,
            "relationships_stored": 6,
        },
    ]

    result = pipeline.process(request)

    assert result.status == PipelineStatus.COMPLETED

    assert result.document_id == request.document_id

    assert result.filename == request.filename

    assert result.chunks_created == 2

    assert result.entities_stored == 9

    assert result.relationships_stored == 9

    assert result.error is None

    ingestion_service.ingest.assert_called_once_with(request)

    document_service.process.assert_called_once()

    chunking_service.chunk_document.assert_called_once_with(
        extracted_document
    )

    assert extraction_service.extract.call_count == 2

    assert graph_ingestion_service.store_extraction.call_count == 2


def test_pipeline_stops_when_ingestion_fails():
    """Test that processing stops if document ingestion fails."""

    (
        pipeline,
        ingestion_service,
        document_service,
        chunking_service,
        extraction_service,
        graph_ingestion_service,
    ) = create_pipeline()

    request = create_request()

    ingestion_service.ingest.return_value = IngestionResult(
        document_id=request.document_id,
        status=IngestionStatus.FAILED,
        error="Unsupported document type.",
    )

    result = pipeline.process(request)

    assert result.status == PipelineStatus.FAILED

    assert result.error == "Unsupported document type."

    assert result.chunks_created == 0

    assert result.entities_stored == 0

    assert result.relationships_stored == 0

    document_service.process.assert_not_called()

    chunking_service.chunk_document.assert_not_called()

    extraction_service.extract.assert_not_called()

    graph_ingestion_service.store_extraction.assert_not_called()


def test_pipeline_handles_extraction_failure():
    """Test that a Gemini extraction failure is reported."""

    (
        pipeline,
        ingestion_service,
        document_service,
        chunking_service,
        extraction_service,
        graph_ingestion_service,
    ) = create_pipeline()

    request = create_request()

    ingestion_service.ingest.return_value = IngestionResult(
        document_id=request.document_id,
        status=IngestionStatus.COMPLETED,
        stored_path="data/uploads/machine_learning.txt",
    )

    document_service.process.return_value = MagicMock()

    chunking_service.chunk_document.return_value = [
        MagicMock(),
    ]

    extraction_service.extract.side_effect = RuntimeError(
        "Gemini extraction failed."
    )

    result = pipeline.process(request)

    assert result.status == PipelineStatus.FAILED

    assert result.chunks_created == 1

    assert result.error == "Gemini extraction failed."

    graph_ingestion_service.store_extraction.assert_not_called()
