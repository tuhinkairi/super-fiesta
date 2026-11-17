"""
Sensitive information redaction.

Removes credentials and secret values from text before logging or reporting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RedactionResult:
    """Result of a sensitive-information redaction operation."""

    original_text: str
    redacted_text: str
    redactions_count: int

    @property
    def was_modified(self) -> bool:
        return self.original_text != self.redacted_text


class SecretRedactor:
    """Detects and redacts common credential patterns."""

    DEFAULT_REPLACEMENT = "[REDACTED]"

    PATTERNS = (
        re.compile(
            r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+"
        ),
        re.compile(
            r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"
        ),
        re.compile(
            r"(?i)((?:api[_-]?key|access[_-]?token|"
            r"auth[_-]?token|client[_-]?secret)\s*[:=]\s*)"
            r"""(["']?)[A-Za-z0-9._~+/=-]{8,}\2"""
        ),
        re.compile(
            r"(?i)((?:password|passwd|secret)\s*[:=]\s*)"
            r"""(["']?)[^\s"',;]{3,}\2"""
        ),
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            r".*?"
            r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            re.DOTALL,
        ),
        re.compile(
            r"\bAIza[0-9A-Za-z_-]{30,}\b"
        ),
        re.compile(
            r"\bsk-[A-Za-z0-9_-]{20,}\b"
        ),
    )

    def __init__(
        self,
        replacement: str = DEFAULT_REPLACEMENT,
    ) -> None:
        if not isinstance(replacement, str) or not replacement:
            raise ValueError("replacement must be a non-empty string.")

        self.replacement = replacement

    def redact(self, text: str) -> RedactionResult:
        """Redact recognized secrets from text."""
        if not isinstance(text, str):
            raise TypeError("text must be a string.")

        redacted = text
        count = 0

        for pattern in self.PATTERNS:
            def replace_match(match: re.Match[str]) -> str:
                nonlocal count
                count += 1

                # Preserve credential labels when the pattern
                # contains a captured prefix.
                if match.lastindex and match.lastindex >= 1:
                    prefix = match.group(1)

                    if prefix:
                        return prefix + self.replacement

                return self.replacement

            redacted = pattern.sub(replace_match, redacted)

        return RedactionResult(
            original_text=text,
            redacted_text=redacted,
            redactions_count=count,
        )

    def redact_many(
        self,
        texts: list[str] | tuple[str, ...],
    ) -> list[RedactionResult]:
        """Redact secrets from multiple text values."""
        if not isinstance(texts, (list, tuple)):
            raise TypeError("texts must be a list or tuple.")

        return [self.redact(text) for text in texts]

    def redact_mapping(
        self,
        values: dict[str, object],
    ) -> dict[str, object]:
        """Recursively redact string values in a mapping."""
        if not isinstance(values, dict):
            raise TypeError("values must be a dictionary.")

        result: dict[str, object] = {}

        for key, value in values.items():
            if isinstance(value, str):
                result[key] = self.redact(value).redacted_text

            elif isinstance(value, dict):
                result[key] = self.redact_mapping(value)

            elif isinstance(value, list):
                result[key] = [
                    self.redact_mapping(item)
                    if isinstance(item, dict)
                    else self.redact(item).redacted_text
                    if isinstance(item, str)
                    else item
                    for item in value
                ]

            else:
                result[key] = value

        return result


def redact_secrets(text: str) -> str:
    """Convenience function returning only the redacted text."""
    return SecretRedactor().redact(text).redacted_text
