from pathlib import Path

from graphrag_app.ingestion.models import IngestionRequest


class DocumentValidator:
    """Validates uploaded documents before ingestion."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
    }

    MAX_FILE_SIZE_MB = 20

    def validate(self, request: IngestionRequest) -> None:
        """Validate the uploaded document.

        Raises:
            ValueError: If the file is invalid or unsupported.
            FileNotFoundError: If the file does not exist.
        """

        file_path = Path(request.file_path)

        # Check whether the file exists.
        if not file_path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        # Ensure the path points to a file.
        if not file_path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        # Validate the file extension.
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: "
                f"{', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        # Validate the file size.
        file_size_mb = file_path.stat().st_size / (
            1024 * 1024
        )

        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File exceeds the maximum size of "
                f"{self.MAX_FILE_SIZE_MB} MB."
            )

        # Validate the filename.
        if not request.filename.strip():
            raise ValueError(
                "Filename cannot be empty."
            )
