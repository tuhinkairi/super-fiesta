
from pathlib import Path


class TXTExtractor:
    """Extracts text from plain-text TXT files."""

    def extract(self, file_path: str | Path) -> str:
        """Read and return the contents of a TXT file."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"TXT document not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        if path.suffix.lower() != ".txt":
            raise ValueError(
                "TXTExtractor only supports .txt files."
            )

        text = path.read_text(encoding="utf-8-sig")

        if not text.strip():
            raise ValueError(
                "The TXT document is empty."
            )

        return text
