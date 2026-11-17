
from pathlib import Path

from graphrag_app.document.txt_extractor import TXTExtractor
from graphrag_app.document.pdf_extractor import PDFExtractor
from graphrag_app.document.docx_extractor import DOCXExtractor


class DocumentExtractor:
    """Selects the appropriate extractor for a document."""

    def __init__(self):
        self._extractors = {
            ".txt": TXTExtractor(),
            ".pdf": PDFExtractor(),
            ".docx": DOCXExtractor(),
        }

    def extract(self, file_path: str | Path) -> str:
        """Extract text using the appropriate file extractor."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        extension = path.suffix.lower()

        extractor = self._extractors.get(extension)

        if extractor is None:
            supported = ", ".join(self._extractors.keys())

            raise ValueError(
                f"Unsupported document extension: {extension}. "
                f"Supported extensions: {supported}"
            )

        return extractor.extract(path)
