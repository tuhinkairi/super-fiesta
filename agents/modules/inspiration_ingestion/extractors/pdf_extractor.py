
from pathlib import Path

import pymupdf  # PyMuPDF


class PDFExtractor:
    """
    Extracts readable text from PDF documents.
    """

    def extract_text(self, pdf_path: str | Path) -> dict:
        """
        Extract text from every page of a PDF.

        Returns:
            A dictionary containing extracted text and page count.
        """

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        if not path.is_file():
            raise ValueError("The provided path is not a file.")

        if path.suffix.lower() != ".pdf":
            raise ValueError("The provided file is not a PDF.")

        try:
            with pymupdf.open(path) as document:
                if document.is_encrypted:
                    raise ValueError("Encrypted PDFs are not supported.")

                pages = []

                for page_number, page in enumerate(document, start=1):
                    page_text = page.get_text("text").strip()

                    if page_text:
                        pages.append(
                            f"--- Page {page_number} ---\n{page_text}"
                        )

                return {
                    "text": "\n\n".join(pages),
                    "page_count": len(document),
                    "has_text": bool(pages),
                }

        except (FileNotFoundError, ValueError):
            raise
        except Exception as error:
            raise RuntimeError(
                f"Failed to extract PDF text: {error}"
            ) from error
