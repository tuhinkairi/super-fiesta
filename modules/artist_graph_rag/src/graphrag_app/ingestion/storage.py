
import shutil
from pathlib import Path
from uuid import uuid4


class DocumentStorage:
    """Handles local storage of uploaded documents."""

    def __init__(
        self,
        storage_dir: str | Path = "data/uploads",
    ):
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(self, source_path: str | Path) -> Path:
        """Save a document and return its stored path."""

        source = Path(source_path)

        if not source.exists() or not source.is_file():
            raise FileNotFoundError(
                f"Source document not found: {source}"
            )

        # Generate a unique filename to avoid collisions.
        unique_filename = (
            f"{uuid4().hex}{source.suffix.lower()}"
        )

        destination = self.storage_dir / unique_filename

        shutil.copy2(source, destination)

        return destination

    def delete(self, file_path: str | Path) -> None:
        """Delete a stored document."""

        target = Path(file_path).resolve()

        # Prevent deletion outside the storage directory.
        if not target.is_relative_to(self.storage_dir):
            raise ValueError(
                "Cannot delete files outside the storage directory."
            )

        if target.exists() and target.is_file():
            target.unlink()

    def exists(self, file_path: str | Path) -> bool:
        """Check whether a stored document exists."""

        target = Path(file_path).resolve()

        if not target.is_relative_to(self.storage_dir):
            return False

        return target.is_file()
