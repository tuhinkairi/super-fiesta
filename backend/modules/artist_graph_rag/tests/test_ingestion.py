
from pathlib import Path

from graphrag_app.ingestion import (
    IngestionRequest,
    IngestionStatus,
    IngestionService,
    DocumentStorage,
)


def test_successful_document_ingestion(tmp_path: Path):
    """Test that a valid document is stored successfully."""

    # Create a temporary source document.
    source_file = tmp_path / "research.txt"
    source_file.write_text(
        "This is a sample research document.",
        encoding="utf-8",
    )

    # Configure temporary storage.
    storage = DocumentStorage(
        storage_dir=tmp_path / "uploads"
    )

    service = IngestionService(storage=storage)

    request = IngestionRequest(
        filename="research.txt",
        file_path=str(source_file),
        content_type="text/plain",
    )

    result = service.ingest(request)

    assert result.status == IngestionStatus.COMPLETED
    assert result.document_id == request.document_id
    assert result.stored_path is not None
    assert Path(result.stored_path).exists()
    assert result.error is None


def test_unsupported_document_type(tmp_path: Path):
    """Test that unsupported file types are rejected."""

    source_file = tmp_path / "research.csv"
    source_file.write_text(
        "name,subject\nAlice,AI",
        encoding="utf-8",
    )

    storage = DocumentStorage(
        storage_dir=tmp_path / "uploads"
    )

    service = IngestionService(storage=storage)

    request = IngestionRequest(
        filename="research.csv",
        file_path=str(source_file),
    )

    result = service.ingest(request)

    assert result.status == IngestionStatus.FAILED
    assert result.error is not None
    assert "Unsupported file type" in result.error
    assert result.stored_path is None


def test_missing_document(tmp_path: Path):
    """Test that a missing document produces a failed result."""

    storage = DocumentStorage(
        storage_dir=tmp_path / "uploads"
    )

    service = IngestionService(storage=storage)

    request = IngestionRequest(
        filename="missing.txt",
        file_path=str(tmp_path / "missing.txt"),
    )

    result = service.ingest(request)

    assert result.status == IngestionStatus.FAILED
    assert result.error is not None
    assert result.stored_path is None
