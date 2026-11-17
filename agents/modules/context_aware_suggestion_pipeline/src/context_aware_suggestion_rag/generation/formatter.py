"""
Content formatting utilities.

Converts generated content into Markdown, plain text, HTML,
and JSON-compatible representations.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
import re
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
)


SUPPORTED_FORMATS = {
    "markdown",
    "plain_text",
    "html",
    "json",
}


@dataclass(frozen=True, slots=True)
class FormattingOptions:
    """Controls how generated content is formatted."""

    include_title: bool = True
    include_description: bool = True
    include_metadata: bool = False
    normalize_whitespace: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "include_title",
            "include_description",
            "include_metadata",
            "normalize_whitespace",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )


class ContentFormatter:
    """Formats generated content into supported output formats."""

    def __init__(
        self,
        options: FormattingOptions | None = None,
    ) -> None:
        self.options = options or FormattingOptions()

    def _normalize(self, text: str) -> str:
        """Normalize whitespace without removing paragraph breaks."""

        if not self.options.normalize_whitespace:
            return text.strip()

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _base_text(self, content: GeneratedContent) -> str:
        """Build the main textual representation."""

        parts: list[str] = []

        if self.options.include_title and content.title:
            parts.append(content.title.strip())

        if self.options.include_description and content.description:
            parts.append(content.description.strip())

        parts.append(self._normalize(content.content))

        return "\n\n".join(parts)

    def to_markdown(
        self,
        content: GeneratedContent,
    ) -> str:
        """Format generated content as Markdown."""

        self._validate_content(content)

        parts: list[str] = []

        if self.options.include_title and content.title:
            parts.append(f"# {content.title.strip()}")

        if self.options.include_description and content.description:
            parts.append(f"*{content.description.strip()}*")

        parts.append(self._normalize(content.content))

        if self.options.include_metadata:
            parts.append(
                self._metadata_markdown(content)
            )

        return "\n\n".join(parts)

    def to_plain_text(
        self,
        content: GeneratedContent,
    ) -> str:
        """Format generated content as plain text."""

        self._validate_content(content)

        parts = [self._base_text(content)]

        if self.options.include_metadata:
            parts.append(
                self._metadata_plain_text(content)
            )

        return "\n\n".join(parts)

    def to_html(
        self,
        content: GeneratedContent,
    ) -> str:
        """Convert generated content into safe basic HTML."""

        self._validate_content(content)

        parts: list[str] = []

        if self.options.include_title and content.title:
            parts.append(
                f"<h1>{escape(content.title.strip())}</h1>"
            )

        if self.options.include_description and content.description:
            parts.append(
                f"<p><em>{escape(content.description.strip())}</em></p>"
            )

        escaped_body = escape(
            self._normalize(content.content)
        )

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                escaped_body,
            )
            if paragraph.strip()
        ]

        for paragraph in paragraphs:
            parts.append(
                f"<p>{paragraph.replace(chr(10), '<br>')}</p>"
            )

        if self.options.include_metadata:
            parts.append(
                self._metadata_html(content)
            )

        return "\n".join(parts)

    def to_dict(
        self,
        content: GeneratedContent,
    ) -> dict[str, Any]:
        """Convert generated content into a JSON-compatible dictionary."""

        self._validate_content(content)

        data: dict[str, Any] = {
            "content_id": content.content_id,
            "request_id": content.request_id,
            "recommendation_id": content.recommendation_id,
            "title": content.title,
            "description": content.description,
            "content": self._normalize(content.content),
            "content_format": content.content_format,
            "model": content.model,
            "language": content.language,
            "word_count": content.word_count,
            "character_count": content.character_count,
            "generated_at": content.generated_at.isoformat(),
        }

        if self.options.include_metadata:
            data["metadata"] = content.metadata.copy()

        return data

    def to_json(
        self,
        content: GeneratedContent,
        *,
        indent: int = 2,
    ) -> str:
        """Serialize generated content as JSON."""

        if (
            isinstance(indent, bool)
            or not isinstance(indent, int)
            or indent < 0
        ):
            raise ValueError(
                "indent must be a non-negative integer."
            )

        return json.dumps(
            self.to_dict(content),
            ensure_ascii=False,
            indent=indent,
        )

    def format(
        self,
        content: GeneratedContent,
        output_format: str = "markdown",
    ) -> str:
        """Format content using the requested output format."""

        output_format = output_format.strip().lower()

        formatters = {
            "markdown": self.to_markdown,
            "plain_text": self.to_plain_text,
            "html": self.to_html,
            "json": self.to_json,
        }

        formatter = formatters.get(output_format)

        if formatter is None:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                f"Supported formats: {sorted(SUPPORTED_FORMATS)}"
            )

        return formatter(content)

    @staticmethod
    def _validate_content(content: GeneratedContent) -> None:
        if not isinstance(content, GeneratedContent):
            raise TypeError(
                "content must be a GeneratedContent instance."
            )

    def _metadata_markdown(
        self,
        content: GeneratedContent,
    ) -> str:
        """Format metadata as a Markdown section."""

        return (
            "## Metadata\n\n"
            f"- Content ID: {content.content_id}\n"
            f"- Model: {content.model}\n"
            f"- Language: {content.language}\n"
            f"- Word count: {content.word_count}"
        )

    def _metadata_plain_text(
        self,
        content: GeneratedContent,
    ) -> str:
        """Format metadata as plain text."""

        return (
            "Metadata\n"
            f"Content ID: {content.content_id}\n"
            f"Model: {content.model}\n"
            f"Language: {content.language}\n"
            f"Word count: {content.word_count}"
        )

    def _metadata_html(
        self,
        content: GeneratedContent,
    ) -> str:
        """Format metadata as safe HTML."""

        return (
            "<section>"
            "<h2>Metadata</h2>"
            "<ul>"
            f"<li>Content ID: {escape(content.content_id)}</li>"
            f"<li>Model: {escape(content.model)}</li>"
            f"<li>Language: {escape(content.language)}</li>"
            f"<li>Word count: {content.word_count}</li>"
            "</ul>"
            "</section>"
        )


def format_generated_content(
    content: GeneratedContent,
    output_format: str = "markdown",
    options: FormattingOptions | None = None,
) -> str:
    """Convenience function for formatting generated content."""

    return ContentFormatter(options).format(
        content,
        output_format,
    )
