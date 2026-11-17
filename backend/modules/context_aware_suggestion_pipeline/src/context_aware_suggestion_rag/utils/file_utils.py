"""Reusable filesystem and file-content utilities."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .validators import validate_non_empty_string, validate_path


def sanitize_filename(
    filename: str,
    *,
    replacement: str = "_",
    max_length: int = 255,
) -> str:
    """Convert a filename into a safe portable filename."""
    filename = validate_non_empty_string(filename, "filename")
    replacement = validate_non_empty_string(replacement, "replacement")

    if isinstance(max_length, bool) or not isinstance(max_length, int):
        raise TypeError("max_length must be an integer.")

    if max_length <= 0:
        raise ValueError("max_length must be greater than zero.")

    if "/" in replacement or "\\" in replacement:
        raise ValueError("replacement cannot contain path separators.")

    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, filename)
    sanitized = sanitized.strip(" .")

    if not sanitized:
        raise ValueError("Filename contains no usable characters.")

    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    stem = Path(sanitized).stem

    if stem.upper() in reserved_names:
        sanitized = f"_{sanitized}"

    if len(sanitized) > max_length:
        suffix = Path(sanitized).suffix
        available_length = max_length - len(suffix)

        if available_length <= 0:
            sanitized = sanitized[:max_length]
        else:
            sanitized = sanitized[:available_length] + suffix

    return sanitized


def calculate_file_hash(
    path: str | Path,
    algorithm: str = "sha256",
    chunk_size: int = 1024 * 1024,
) -> str:
    """Calculate a hexadecimal hash of a file."""
    file_path = validate_path(path, must_exist=True, must_be_file=True)
    algorithm = validate_non_empty_string(algorithm, "algorithm").lower()

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    try:
        digest = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}") from exc

    with file_path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def read_text_file(
    path: str | Path,
    encoding: str = "utf-8",
) -> str:
    """Read a text file using the specified encoding."""
    file_path = validate_path(path, must_exist=True, must_be_file=True)
    encoding = validate_non_empty_string(encoding, "encoding")

    try:
        return file_path.read_text(encoding=encoding)
    except (UnicodeError, OSError) as exc:
        raise OSError(f"Unable to read text file: {file_path}") from exc


def write_text_file(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
    *,
    create_parent: bool = True,
) -> Path:
    """Write text to a file, optionally creating its parent directory."""
    file_path = validate_path(path)
    encoding = validate_non_empty_string(encoding, "encoding")

    if not isinstance(content, str):
        raise TypeError("content must be a string.")

    if not isinstance(create_parent, bool):
        raise TypeError("create_parent must be a boolean.")

    if create_parent:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding=encoding)
    return file_path


def read_json_file(
    path: str | Path,
    encoding: str = "utf-8",
) -> Any:
    """Read and deserialize a JSON file."""
    content = read_text_file(path, encoding)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in file {path}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from exc


def write_json_file(
    path: str | Path,
    data: Any,
    encoding: str = "utf-8",
    *,
    indent: int = 2,
    create_parent: bool = True,
) -> Path:
    """Serialize data as JSON and write it to a file."""
    if isinstance(indent, bool) or not isinstance(indent, int):
        raise TypeError("indent must be an integer.")

    if indent < 0:
        raise ValueError("indent must not be negative.")

    try:
        content = json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Data cannot be serialized as valid JSON.") from exc

    return write_text_file(
        path,
        content,
        encoding,
        create_parent=create_parent,
    )


def atomic_write_text(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> Path:
    """Atomically replace a text file using a temporary file."""
    file_path = validate_path(path)
    encoding = validate_non_empty_string(encoding, "encoding")

    if not isinstance(content, str):
        raise TypeError("content must be a string.")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, file_path)
        return file_path

    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def atomic_write_json(
    path: str | Path,
    data: Any,
    encoding: str = "utf-8",
    *,
    indent: int = 2,
) -> Path:
    """Atomically serialize and write JSON."""
    if isinstance(indent, bool) or not isinstance(indent, int):
        raise TypeError("indent must be an integer.")

    if indent < 0:
        raise ValueError("indent must not be negative.")

    try:
        content = json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Data cannot be serialized as valid JSON.") from exc

    return atomic_write_text(path, content, encoding)


def get_file_extension(path: str | Path) -> str:
    """Return a lowercase file extension without the leading dot."""
    file_path = validate_path(path)
    return file_path.suffix.lower().lstrip(".")


def get_file_size_bytes(path: str | Path) -> int:
    """Return the size of an existing file in bytes."""
    file_path = validate_path(path, must_exist=True, must_be_file=True)
    return file_path.stat().st_size


def copy_file(
    source: str | Path,
    destination: str | Path,
    *,
    create_parent: bool = True,
) -> Path:
    """Copy a file's bytes to a destination."""
    import shutil

    source_path = validate_path(
        source,
        field_name="source",
        must_exist=True,
        must_be_file=True,
    )
    destination_path = validate_path(destination, field_name="destination")

    if source_path.resolve() == destination_path.resolve():
        raise ValueError("Source and destination must be different.")

    if create_parent:
        destination_path.parent.mkdir(parents=True, exist_ok=True)

    if not destination_path.parent.exists():
        raise FileNotFoundError(
            f"Destination directory does not exist: {destination_path.parent}"
        )

    shutil.copy2(source_path, destination_path)
    return destination_path
