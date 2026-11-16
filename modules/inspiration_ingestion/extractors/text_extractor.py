
from pathlib import Path


class TextExtractor:
    """
    Extracts readable content from TXT and Markdown files.
    """

    SUPPORTED_EXTENSIONS = {".txt", ".md"}

    def extract_text(self, file_path: str | Path) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError("The provided path is not a file.")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Only TXT and Markdown files are supported.")

        try:
            content = path.read_text(encoding="utf-8-sig")

            return {
                "file_name": path.name,
                "text": content.strip(),
                "character_count": len(content.strip()),
                "word_count": len(content.split()),
            }

        except UnicodeDecodeError as error:
            raise ValueError(
                "File must contain valid UTF-8 text."
            ) from error
