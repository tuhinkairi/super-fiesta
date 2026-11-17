
from pathlib import Path

from pypdf import PdfReader


class PDFExtractor:
    """Extracts text from PDF documents."""

    def extract(self, file_path: str | Path) -> str:
        """Read and return text from a PDF document."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF document not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "PDFExtractor only supports .pdf files."
            )

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDF documents are not supported."
            )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()

            if page_text and page_text.strip():
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{page_text}"
                )

        text = "\n".join(extracted_pages).strip()

        if not text:
            raise ValueError(
                "No readable text found in the PDF document. "
                "It may be a scanned PDF requiring OCR."
            )

        return text
