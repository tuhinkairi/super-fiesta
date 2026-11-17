"""
Document ingestion validators.

Performs document-specific validation before files enter
the ingestion pipeline.
"""

from pathlib import Path

from context_aware_suggestion_rag.config.settings import get_settings
from context_aware_suggestion_rag.constants import SUPPORTED_DOCUMENT_EXTENSIONS
from context_aware_suggestion_rag.core.paths import (
    get_file_size,
    is_file,
    resolve_path,
)
from context_aware_suggestion_rag.core.validators import (
    validate_document_content,
    validate_document_extension,
    validate_identifier,
)
from context_aware_suggestion_rag.exceptions import (
    DocumentValidationError,
)


def validate_file_path(file_path: str | Path) -> Path:
    """Validate a local document file path."""

    try:
        path = resolve_path(file_path)
    except (TypeError, ValueError, OSError) as exc:
        raise DocumentValidationError(
            "Invalid document file path."
        ) from exc

    if not path.exists():
        raise DocumentValidationError(
            f"Document does not exist: {path}"
        )

    if not is_file(path):
        raise DocumentValidationError(
            f"Expected a regular file: {path}"
        )

    return path


def validate_file_extension(file_path: str | Path) -> str:
    """Validate and return a supported document extension."""

    filename = Path(file_path).name

    try:
        extension = validate_document_extension(filename)
    except ValueError as exc:
        raise DocumentValidationError(str(exc)) from exc

    if extension not in SUPPORTED_DOCUMENT_EXTENSIONS:
        raise DocumentValidationError(
            f"Unsupported document extension: {extension}"
        )

    return extension


def validate_file_size(file_path: str | Path) -> int:
    """Validate document size against the configured size limit."""

    path = validate_file_path(file_path)

    try:
        size_bytes = get_file_size(path)
    except OSError as exc:
        raise DocumentValidationError(
            "Unable to determine document size."
        ) from exc

    maximum_bytes = (
        get_settings().max_document_size_mb * 1024 * 1024
    )

    if size_bytes > maximum_bytes:
        raise DocumentValidationError(
            f"Document exceeds the maximum size of "
            f"{get_settings().max_document_size_mb} MB."
        )

    if size_bytes == 0:
        raise DocumentValidationError(
            "Document file is empty."
        )

    return size_bytes


def validate_document_file(file_path: str | Path) -> Path:
    """Run all file-level validation checks."""

    path = validate_file_path(file_path)
    validate_file_extension(path)
    validate_file_size(path)

    return path


def validate_document_name(filename: str) -> str:
    """Validate a document filename."""

    if not isinstance(filename, str):
        raise DocumentValidationError(
            "Document filename must be a string."
        )

    filename = filename.strip()

    if not filename:
        raise DocumentValidationError(
            "Document filename cannot be empty."
        )

    if Path(filename).name != filename:
        raise DocumentValidationError(
            "Document filename must not contain directory paths."
        )

    validate_file_extension(filename)

    return filename


def validate_document_text(content: str) -> str:
    """Validate extracted document text."""

    try:
        return validate_document_content(content)
    except ValueError as exc:
        raise DocumentValidationError(str(exc)) from exc


def validate_document_id(document_id: str) -> str:
    """Validate a document identifier."""

    try:
        return validate_identifier(
            document_id,
            field_name="document_id",
        )
    except ValueError as exc:
        raise DocumentValidationError(str(exc)) from exc


__all__ = [
    "validate_file_path",
    "validate_file_extension",
    "validate_file_size",
    "validate_document_file",
    "validate_document_name",
    "validate_document_text",
    "validate_document_id",
]
