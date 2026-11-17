
import shutil
from pathlib import Path
from uuid import uuid4

from modules.inspiration_ingestion.config import (
    get_inspiration_settings,
)


class FileHandler:
    """
    Validates and stores uploaded inspiration files.
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf": "pdf",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".webp": "image",
        ".gif": "image",
        ".txt": "text",
        ".md": "text",
    }

    def __init__(self):
        self.settings = get_inspiration_settings()
        self.originals_dir = self.settings.storage_dir / "originals"

    def validate_file(self, source_path: str | Path) -> tuple[Path, str]:
        """
        Check that the file exists, has a supported extension,
        and does not exceed the configured size limit.
        """

        path = Path(source_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError("The provided path is not a file.")

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension or 'no extension'}"
            )

        max_size_bytes = self.settings.max_file_size_mb * 1024 * 1024

        if path.stat().st_size > max_size_bytes:
            raise ValueError(
                f"File exceeds the {self.settings.max_file_size_mb} MB limit."
            )

        return path, self.SUPPORTED_EXTENSIONS[extension]

    def save_file(self, source_path: str | Path) -> dict:
        """
        Validate a file and save a uniquely named copy
        in the appropriate originals folder.
        """

        source, content_type = self.validate_file(source_path)

        destination_dir = self.originals_dir / {
            "pdf": "pdfs",
            "image": "images",
            "text": "texts",
        }[content_type]

        destination_dir.mkdir(parents=True, exist_ok=True)

        # Generate a unique name to avoid overwriting files.
        unique_name = f"{uuid4().hex}{source.suffix.lower()}"
        destination_path = destination_dir / unique_name

        shutil.copy2(source, destination_path)

        return {
            "file_name": source.name,
            "stored_name": unique_name,
            "content_type": content_type,
            "storage_path": str(destination_path.resolve()),
            "file_size_bytes": destination_path.stat().st_size,
        }
