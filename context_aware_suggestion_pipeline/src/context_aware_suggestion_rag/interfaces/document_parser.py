"""
Document parser interfaces.

Defines a common contract for extracting text and metadata
from supported document formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping


class DocumentParser(ABC):
    """Abstract contract for document format parsers."""

    @abstractmethod
    def parse(self, file_path: str | Path) -> str:
        """Extract textual content from a document."""
        raise NotImplementedError

    @abstractmethod
    def supports(self, file_path: str | Path) -> bool:
        """Return whether this parser supports the given file."""
        raise NotImplementedError

    def extract_metadata(
        self,
        file_path: str | Path,
    ) -> Mapping[str, Any]:
        """Extract optional document metadata."""
        return {}

    def validate(self, file_path: str | Path) -> bool:
        """Check that the supplied path is a readable file."""
        path = Path(file_path).expanduser()

        return path.exists() and path.is_file()
