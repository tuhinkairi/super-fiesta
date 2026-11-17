"""
Input sanitization utilities.

Provides reusable text sanitization operations and structured
sanitization results for the security package.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from context_aware_suggestion_rag.security.models import SanitizationResult


# ============================================================
# Configuration
# ============================================================

@dataclass(frozen=True, slots=True)
class SanitizationConfig:
    """Configuration for text sanitization."""

    remove_null_bytes: bool = True
    remove_control_characters: bool = True
    preserve_newlines: bool = True
    preserve_tabs: bool = True
    normalize_whitespace: bool = False
    strip_whitespace: bool = True

    def __post_init__(self) -> None:
        for name in (
            "remove_null_bytes",
            "remove_control_characters",
            "preserve_newlines",
            "preserve_tabs",
            "normalize_whitespace",
            "strip_whitespace",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean.")


# ============================================================
# Text Sanitizer
# ============================================================

class TextSanitizer:
    """Sanitizes text by removing unsafe control characters."""

    def __init__(
        self,
        config: SanitizationConfig | None = None,
    ) -> None:
        self.config = config or SanitizationConfig()

    def sanitize(self, value: str) -> SanitizationResult:
        """
        Sanitize a text value.

        This operation does not perform HTML escaping, SQL escaping,
        shell escaping, or other context-specific output encoding.
        """
        if not isinstance(value, str):
            raise TypeError("value must be a string.")

        sanitized = value
        warnings: list[str] = []

        # Remove null bytes.
        if self.config.remove_null_bytes and "\x00" in sanitized:
            sanitized = sanitized.replace("\x00", "")
            warnings.append("Null bytes were removed.")

        # Normalize line endings.
        if self.config.preserve_newlines:
            normalized = sanitized.replace("\r\n", "\n").replace("\r", "\n")

            if normalized != sanitized:
                warnings.append("Line endings were normalized.")

            sanitized = normalized

        # Remove unwanted control characters.
        if self.config.remove_control_characters:
            cleaned_characters: list[str] = []
            removed_control = False

            for character in sanitized:
                category = unicodedata.category(character)

                if category == "Cc":
                    allowed = (
                        (character == "\n" and self.config.preserve_newlines)
                        or (character == "\t" and self.config.preserve_tabs)
                    )

                    if allowed:
                        cleaned_characters.append(character)
                    else:
                        removed_control = True
                else:
                    cleaned_characters.append(character)

            sanitized = "".join(cleaned_characters)

            if removed_control:
                warnings.append("Control characters were removed.")

        # Optionally replace tabs and repeated whitespace.
        if self.config.normalize_whitespace:
            if not self.config.preserve_tabs:
                sanitized = sanitized.replace("\t", " ")

            if self.config.preserve_newlines:
                lines = sanitized.split("\n")
                sanitized = "\n".join(
                    re.sub(r"[^\S\n]+", " ", line).strip()
                    for line in lines
                )
            else:
                sanitized = re.sub(r"\s+", " ", sanitized)

            warnings.append("Whitespace normalization was enabled.")

        if self.config.strip_whitespace:
            stripped = sanitized.strip()

            if stripped != sanitized:
                warnings.append("Leading or trailing whitespace was removed.")

            sanitized = stripped

        return SanitizationResult(
            original_value=value,
            sanitized_value=sanitized,
            modified=(value != sanitized),
            warnings=warnings,
            metadata={
                "sanitizer": self.__class__.__name__,
                "original_length": len(value),
                "sanitized_length": len(sanitized),
            },
        )


# ============================================================
# Convenience Function
# ============================================================

def sanitize_text(
    value: str,
    config: SanitizationConfig | None = None,
) -> SanitizationResult:
    """Sanitize text using the default or supplied configuration."""
    return TextSanitizer(config=config).sanitize(value)
