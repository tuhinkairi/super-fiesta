from datetime import datetime, timezone

from graphrag_app.ingestion.models import (
    IngestionRequest,
    IngestionResult,
    IngestionStatus,
)
from graphrag_app.ingestion.validator import DocumentValidator
from graphrag_app.ingestion.storage import DocumentStorage


class IngestionService:
    """Coordinates document validation and storage."""

    def __init__(
        self,
        validator: DocumentValidator | None = None,
        storage: DocumentStorage | None = None,
    ):
        self.validator = validator or DocumentValidator()
        self.storage = storage or DocumentStorage()

    def ingest(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Validate and store an uploaded document."""

        try:
            # Step 1: Validate the original document.
            self.validator.validate(request)

            # Step 2: Store the document.
            stored_path = self.storage.save(
                request.file_path
            )

            # Step 3: Return the successful result.
            return IngestionResult(
                document_id=request.document_id,
                status=IngestionStatus.COMPLETED,
                message="Document successfully stored.",
                processed_at=datetime.now(timezone.utc),
                stored_path=str(stored_path),
            )

        except Exception as error:
            # Return a failed ingestion result.
            return IngestionResult(
                document_id=request.document_id,
                status=IngestionStatus.FAILED,
                message="Document ingestion failed.",
                processed_at=datetime.now(timezone.utc),
                error=str(error),
            )
