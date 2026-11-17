"""Reusable directory-management utilities."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterator

from .validators import validate_non_empty_string, validate_path


def create_directory(
    path: str | Path,
    *,
    parents: bool = True,
    exist_ok: bool = True,
) -> Path:
    """Create a directory and return its resolved path."""
    directory = validate_path(path)

    if not isinstance(parents, bool):
        raise TypeError("parents must be a boolean.")

    if not isinstance(exist_ok, bool):
        raise TypeError("exist_ok must be a boolean.")

    directory.mkdir(parents=parents, exist_ok=exist_ok)
    return directory.resolve()


def ensure_directory(path: str | Path) -> Path:
    """Ensure that a directory exists."""
    directory = validate_path(path)

    if directory.exists() and not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    directory.mkdir(parents=True, exist_ok=True)
    return directory.resolve()


def list_files(
    directory: str | Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
) -> list[Path]:
    """List files in a directory."""
    root = validate_path(
        directory,
        field_name="directory",
        must_exist=True,
        must_be_directory=True,
    )

    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean.")

    if not isinstance(include_hidden, bool):
        raise TypeError("include_hidden must be a boolean.")

    iterator = root.rglob("*") if recursive else root.iterdir()

    files = [
        path
        for path in iterator
        if path.is_file()
        and (
            include_hidden
            or not any(part.startswith(".") for part in path.relative_to(root).parts)
        )
    ]

    return sorted(files)


def iter_files(
    directory: str | Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
) -> Iterator[Path]:
    """Iterate over files in a directory."""
    yield from list_files(
        directory,
        recursive=recursive,
        include_hidden=include_hidden,
    )


def find_files_by_extension(
    directory: str | Path,
    extensions: str | list[str] | tuple[str, ...] | set[str],
    *,
    recursive: bool = True,
    case_sensitive: bool = False,
) -> list[Path]:
    """Find files matching one or more extensions."""
    root = validate_path(
        directory,
        field_name="directory",
        must_exist=True,
        must_be_directory=True,
    )

    if isinstance(extensions, str):
        extension_values = [extensions]
    elif isinstance(extensions, (list, tuple, set)):
        extension_values = list(extensions)
    else:
        raise TypeError("extensions must be a string or a collection of strings.")

    if not extension_values:
        raise ValueError("At least one extension must be provided.")

    normalized_extensions = set()

    for extension in extension_values:
        extension = validate_non_empty_string(extension, "extension")
        normalized = extension if case_sensitive else extension.lower()

        if not normalized.startswith("."):
            normalized = f".{normalized}"

        normalized_extensions.add(normalized)

    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean.")

    if not isinstance(case_sensitive, bool):
        raise TypeError("case_sensitive must be a boolean.")

    files = list_files(root, recursive=recursive)

    if case_sensitive:
        return [
            path for path in files
            if path.suffix in normalized_extensions
        ]

    return [
        path for path in files
        if path.suffix.lower() in normalized_extensions
    ]


def directory_size_bytes(
    directory: str | Path,
    *,
    recursive: bool = True,
) -> int:
    """Calculate the total size of files in a directory."""
    root = validate_path(
        directory,
        field_name="directory",
        must_exist=True,
        must_be_directory=True,
    )

    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean.")

    files = list_files(root, recursive=recursive)

    total_size = 0

    for file_path in files:
        try:
            total_size += file_path.stat().st_size
        except OSError:
            continue

    return total_size


def count_files(
    directory: str | Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
) -> int:
    """Count files in a directory."""
    return len(
        list_files(
            directory,
            recursive=recursive,
            include_hidden=include_hidden,
        )
    )


def directory_exists(path: str | Path) -> bool:
    """Check whether a path exists and is a directory."""
    directory = validate_path(path)
    return directory.is_dir()


def remove_directory(
    path: str | Path,
    *,
    recursive: bool = False,
    missing_ok: bool = False,
) -> bool:
    """Remove a directory, optionally including its contents."""
    directory = validate_path(path)

    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean.")

    if not isinstance(missing_ok, bool):
        raise TypeError("missing_ok must be a boolean.")

    if not directory.exists():
        if missing_ok:
            return False

        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    if recursive:
        shutil.rmtree(directory)
    else:
        directory.rmdir()

    return True


def get_relative_path(
    path: str | Path,
    base_directory: str | Path,
) -> Path:
    """Return a path relative to a base directory."""
    target = validate_path(path, field_name="path")
    base = validate_path(base_directory, field_name="base_directory")

    try:
        return target.resolve().relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Path '{target}' is outside base directory '{base}'."
        ) from exc


def get_directory_tree(
    directory: str | Path,
    *,
    max_depth: int | None = None,
) -> dict[str, object]:
    """Build a nested dictionary representing a directory tree."""
    root = validate_path(
        directory,
        field_name="directory",
        must_exist=True,
        must_be_directory=True,
    )

    if max_depth is not None:
        if isinstance(max_depth, bool) or not isinstance(max_depth, int):
            raise TypeError("max_depth must be an integer or None.")

        if max_depth < 0:
            raise ValueError("max_depth must not be negative.")

    def build_tree(current: Path, depth: int) -> dict[str, object]:
        result: dict[str, object] = {}

        if max_depth is not None and depth >= max_depth:
            return result

        for child in sorted(current.iterdir(), key=lambda item: item.name.lower()):
            if child.name.startswith("."):
                continue

            if child.is_dir():
                result[child.name] = build_tree(child, depth + 1)
            elif child.is_file():
                result[child.name] = child.stat().st_size

        return result

    return {
        root.name: build_tree(root, 0)
    }
