"""
Document loaders.

Extracts text from PDF, DOCX, TXT, and JSON documents and
returns a standardized ExtractionResult.
"""

import json
import time
from pathlib import Path
from zipfile import BadZipFile

from docx import Document
from pypdf import PdfReader

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.text import normalize_text
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import DocumentType
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import (
    DocumentLoadError,
    DocumentValidationError,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.models import ExtractionResult
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.validators import (
    validate_document_file,
)


class DocumentLoader:
    """Loads supported documents and extracts their text."""

    def load(self, file_path: str | Path) -> ExtractionResult:
        """
        Validate a file, extract its text, and return an extraction result.

        Args:
            file_path: Path to the document.

        Returns:
            A standardized ExtractionResult.

        Raises:
            DocumentValidationError: If file validation fails.
            DocumentLoadError: If document extraction fails.
        """
        path = validate_document_file(file_path)

        extension = path.suffix.lower()
        document_type = DocumentType(extension.lstrip("."))

        start_time = time.perf_counter()
        warnings: list[str] = []
        total_pages: int | None = None

        try:
            if document_type == DocumentType.PDF:
                extracted_text, total_pages, warnings = self._load_pdf(path)

            elif document_type == DocumentType.DOCX:
                extracted_text = self._load_docx(path)

            elif document_type == DocumentType.TXT:
                extracted_text = self._load_txt(path)

            elif document_type == DocumentType.JSON:
                extracted_text = self._load_json(path)

            else:
                raise DocumentLoadError(
                    f"Unsupported document type: {document_type}"
                )

        except DocumentLoadError:
            raise
        except (OSError, UnicodeError, ValueError, BadZipFile) as exc:
            raise DocumentLoadError(
                f"Failed to extract text from '{path.name}': {exc}"
            ) from exc
        except Exception as exc:
            raise DocumentLoadError(
                f"Unexpected error while loading '{path.name}': {exc}"
            ) from exc

        extracted_text = normalize_text(extracted_text)

        if not extracted_text.strip():
            warnings.append(
                "No extractable text was found in the document."
            )

        extraction_time = time.perf_counter() - start_time

        return ExtractionResult(
            filename=path.name,
            document_type=document_type,
            extracted_text=extracted_text,
            total_pages=total_pages,
            total_characters=len(extracted_text),
            extraction_time_seconds=extraction_time,
            warnings=warnings,
        )

    @staticmethod
    def _load_pdf(
        path: Path,
    ) -> tuple[str, int, list[str]]:
        """Extract text from every page of a PDF document."""

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise DocumentLoadError(
                f"Encrypted PDF documents are not supported: {path.name}"
            )

        pages: list[str] = []
        warnings: list[str] = []

        total_pages = len(reader.pages)

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:
                warnings.append(
                    f"Could not extract text from PDF page "
                    f"{page_number}: {exc}"
                )
                continue

            if not page_text.strip():
                warnings.append(
                    f"PDF page {page_number} contains no extractable text."
                )
                continue

            pages.append(page_text)

        return "\n\n".join(pages), total_pages, warnings

    @staticmethod
    def _load_docx(path: Path) -> str:
        """Extract paragraphs and table contents from a DOCX document."""

        document = Document(str(path))
        sections: list[str] = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                sections.append(text)

        for table_index, table in enumerate(document.tables, start=1):
            sections.append(f"Table {table_index}:")

            for row in table.rows:
                cells = [
                    cell.text.strip().replace("\n", " ")
                    for cell in row.cells
                ]

                if any(cells):
                    sections.append(" | ".join(cells))

        return "\n\n".join(sections)

    @staticmethod
    def _load_txt(path: Path) -> str:
        """Read a UTF-8 text document."""

        return path.read_text(encoding="utf-8-sig")

    @staticmethod
    def _load_json(path: Path) -> str:
        """Parse JSON and convert it into structured readable text."""

        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        return json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


# Shared convenience function for other package components.
_default_loader = DocumentLoader()


def load_document(file_path: str | Path) -> ExtractionResult:
    """Load a document using the default DocumentLoader."""
    return _default_loader.load(file_path)


__all__ = [
    "DocumentLoader",
    "load_document",
]
