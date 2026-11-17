from pathlib import Path

from modules.artist_graph_rag.src.graphrag_app.document.models import ExtractedDocument
from modules.artist_graph_rag.src.graphrag_app.document.extractor import (
    DocumentExtractor,
)
from modules.artist_graph_rag.src.graphrag_app.document.cleaner import TextCleaner


class DocumentService:
    """Coordinates document extraction and text cleaning."""

    def __init__(
        self,
        extractor: DocumentExtractor | None = None,
        cleaner: TextCleaner | None = None,
    ):
        self.extractor = extractor or DocumentExtractor()
        self.cleaner = cleaner or TextCleaner()

    def process(
        self,
        file_path: str | Path,
        document_id: str,
        filename: str | None = None,
    ) -> ExtractedDocument:
        """Extract and clean a document.

        Args:
            file_path: Path to the stored document.
            document_id: ID assigned during ingestion.
            filename: Original document filename.

        Returns:
            A structured ExtractedDocument object.
        """

        path = Path(file_path)

        if not document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Document not found: {path}")

        # Step 1: Extract text.
        raw_text = self.extractor.extract(path)

        # Step 2: Clean extracted text.
        cleaned_text = self.cleaner.clean(raw_text)

        # Step 3: Reject documents with no usable content.
        if not cleaned_text:
            raise ValueError("Document contains no usable text.")

        # Step 4: Build structured document data.
        return ExtractedDocument(
            document_id=document_id,
            filename=filename or path.name,
            text=cleaned_text,
            character_count=len(cleaned_text),
            page_count=None,
            metadata={
                "file_extension": path.suffix.lower(),
                "file_size_bytes": path.stat().st_size,
            },
        )
