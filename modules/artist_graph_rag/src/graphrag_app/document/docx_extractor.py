from pathlib import Path

from docx import Document


class DOCXExtractor:
    """Extracts text from Microsoft Word DOCX documents."""

    def extract(self, file_path: str | Path) -> str:
        """Read and return text from a DOCX document."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"DOCX document not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        if path.suffix.lower() != ".docx":
            raise ValueError(
                "DOCXExtractor only supports .docx files."
            )

        document = Document(str(path))

        extracted_parts = []

        # Extract paragraphs.
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_parts.append(text)

        # Extract text from tables.
        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                row_text = " | ".join(
                    cell for cell in cells if cell
                )

                if row_text:
                    extracted_parts.append(row_text)

        text = "\n\n".join(extracted_parts).strip()

        if not text:
            raise ValueError(
                "No readable text found in the DOCX document."
            )

        return text
