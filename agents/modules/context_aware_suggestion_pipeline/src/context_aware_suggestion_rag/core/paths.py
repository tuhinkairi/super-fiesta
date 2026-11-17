"""
Centralized filesystem path utilities.

Provides safe, reusable directory and file path management
for the Context-Aware Suggestion RAG package.
"""

from pathlib import Path


def resolve_path(path: str | Path) -> Path:
    """Expand and resolve a filesystem path."""

    if not isinstance(path, (str, Path)):
        raise TypeError("path must be a string or Path object")

    if not str(path).strip():
        raise ValueError("path cannot be empty")

    return Path(path).expanduser().resolve()


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not already exist."""

    directory = resolve_path(path)
    directory.mkdir(parents=True, exist_ok=True)

    return directory


def ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory of a file path."""

    file_path = resolve_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    return file_path


def path_exists(path: str | Path) -> bool:
    """Check whether a filesystem path exists."""

    return resolve_path(path).exists()


def is_file(path: str | Path) -> bool:
    """Check whether a path points to an existing file."""

    return resolve_path(path).is_file()


def is_directory(path: str | Path) -> bool:
    """Check whether a path points to an existing directory."""

    return resolve_path(path).is_dir()


def get_file_extension(path: str | Path) -> str:
    """Return the lowercase file extension."""

    return resolve_path(path).suffix.lower()


def get_file_size(path: str | Path) -> int:
    """Return file size in bytes."""

    file_path = resolve_path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    return file_path.stat().st_size


def get_project_root() -> Path:
    """
    Return the project root directory.

    This module is located under:
    project_root/src/context_aware_suggestion_rag/core/
    """

    return Path(__file__).resolve().parents[4]


def get_package_root() -> Path:
    """Return the installed package source directory."""

    return Path(__file__).resolve().parents[1]


def get_default_data_directory() -> Path:
    """Return the default project data directory."""

    return get_project_root() / "data"


def get_default_cache_directory() -> Path:
    """Return the default project cache directory."""

    return get_default_data_directory() / "cache"


def get_default_log_directory() -> Path:
    """Return the default project log directory."""

    return get_project_root() / "logs"


__all__ = [
    "resolve_path",
    "ensure_directory",
    "ensure_parent_directory",
    "path_exists",
    "is_file",
    "is_directory",
    "get_file_extension",
    "get_file_size",
    "get_project_root",
    "get_package_root",
    "get_default_data_directory",
    "get_default_cache_directory",
    "get_default_log_directory",
]
