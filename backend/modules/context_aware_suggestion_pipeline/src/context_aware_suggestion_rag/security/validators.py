"""
Security validation utilities.

Provides reusable validation for untrusted input entering the pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.security.models import (
    SecurityValidationResult,
)


# ============================================================
# Configuration
# ============================================================

@dataclass(frozen=True, slots=True)
class SecurityValidationConfig:
    """Configuration for security input validation."""

    max_input_length: int = 100_000
    max_url_length: int = 2_048
    allow_urls: bool = True
    allow_html: bool = False
    reject_null_bytes: bool = True
    reject_control_characters: bool = True
    check_prompt_injection: bool = True
    check_suspicious_urls: bool = True
    allowed_url_schemes: tuple[str, ...] = ("http", "https")

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_input_length, bool)
            or not isinstance(self.max_input_length, int)
            or self.max_input_length <= 0
        ):
            raise ValueError("max_input_length must be a positive integer.")

        if (
            isinstance(self.max_url_length, bool)
            or not isinstance(self.max_url_length, int)
            or self.max_url_length <= 0
        ):
            raise ValueError("max_url_length must be a positive integer.")

        for name in (
            "allow_urls",
            "allow_html",
            "reject_null_bytes",
            "reject_control_characters",
            "check_prompt_injection",
            "check_suspicious_urls",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean.")

        if not isinstance(self.allowed_url_schemes, tuple):
            raise TypeError("allowed_url_schemes must be a tuple.")

        if not all(
            isinstance(scheme, str) and scheme.strip()
            for scheme in self.allowed_url_schemes
        ):
            raise ValueError("URL schemes must be non-empty strings.")


# ============================================================
# Validator
# ============================================================

class SecurityInputValidator:
    """Validates untrusted text and URL inputs."""

    _PROMPT_INJECTION_PATTERNS = (
        re.compile(
            r"ignore\s+(all\s+)?previous\s+instructions",
            re.IGNORECASE,
        ),
        re.compile(
            r"ignore\s+(all\s+)?prior\s+instructions",
            re.IGNORECASE,
        ),
        re.compile(
            r"reveal\s+(your\s+)?(system\s+)?prompt",
            re.IGNORECASE,
        ),
        re.compile(
            r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
            re.IGNORECASE,
        ),
        re.compile(
            r"bypass\s+(all\s+)?(safety|security)\s+(rules|filters)",
            re.IGNORECASE,
        ),
    )

    _SUSPICIOUS_URL_PATTERNS = (
        re.compile(r"javascript\s*:", re.IGNORECASE),
        re.compile(r"data\s*:", re.IGNORECASE),
        re.compile(r"vbscript\s*:", re.IGNORECASE),
        re.compile(r"@.*@", re.IGNORECASE),
    )

    def __init__(
        self,
        config: SecurityValidationConfig | None = None,
    ) -> None:
        self.config = config or SecurityValidationConfig()

    def validate(self, value: Any) -> SecurityValidationResult:
        """Validate a text input and return a structured result."""

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(value, str):
            return SecurityValidationResult(
                valid=False,
                errors=["Input must be a string."],
            )

        if not value.strip():
            errors.append("Input cannot be empty.")

        if len(value) > self.config.max_input_length:
            errors.append(
                f"Input exceeds maximum length of "
                f"{self.config.max_input_length} characters."
            )

        if self.config.reject_null_bytes and "\x00" in value:
            errors.append("Input contains null bytes.")

        if self.config.reject_control_characters:
            if any(
                ord(char) < 32 and char not in "\n\r\t"
                for char in value
            ):
                errors.append("Input contains control characters.")

        if not self.config.allow_html:
            if re.search(r"<[^>]+>", value):
                warnings.append(
                    "Input contains HTML-like markup."
                )

        if self.config.check_prompt_injection:
            if self._contains_prompt_injection(value):
                warnings.append(
                    "Input contains a potential prompt-injection pattern."
                )

        if self.config.check_suspicious_urls:
            for suspicious_pattern in self._SUSPICIOUS_URL_PATTERNS:
                if suspicious_pattern.search(value):
                    warnings.append(
                        "Input contains a potentially suspicious URL pattern."
                    )
                    break

        return SecurityValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            metadata={
                "input_length": len(value),
                "validator": self.__class__.__name__,
            },
        )

    def validate_url(self, url: str) -> SecurityValidationResult:
        """Validate a URL's basic structure and scheme."""

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(url, str):
            return SecurityValidationResult(
                valid=False,
                errors=["URL must be a string."],
            )

        if not url.strip():
            errors.append("URL cannot be empty.")
        elif len(url) > self.config.max_url_length:
            errors.append(
                f"URL exceeds maximum length of "
                f"{self.config.max_url_length} characters."
            )
        elif not self.config.allow_urls:
            errors.append("URLs are not allowed by configuration.")
        else:
            try:
                parsed = urlsplit(url.strip())

                if parsed.scheme.lower() not in {
                    scheme.lower()
                    for scheme in self.config.allowed_url_schemes
                }:
                    errors.append("URL scheme is not allowed.")

                if not parsed.hostname:
                    errors.append("URL must contain a valid hostname.")

                if parsed.username or parsed.password:
                    warnings.append(
                        "URL contains embedded user credentials."
                    )

                if parsed.port is not None and not (
                    1 <= parsed.port <= 65535
                ):
                    errors.append("URL port is invalid.")

            except ValueError:
                errors.append("URL structure is invalid.")

        return SecurityValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            metadata={
                "validator": self.__class__.__name__,
                "input_type": "url",
            },
        )

    @classmethod
    def _contains_prompt_injection(cls, value: str) -> bool:
        """Detect common prompt-injection phrases."""
        return any(
            pattern.search(value)
            for pattern in cls._PROMPT_INJECTION_PATTERNS
        )


# ============================================================
# Convenience Functions
# ============================================================

def validate_security_input(
    value: Any,
    config: SecurityValidationConfig | None = None,
) -> SecurityValidationResult:
    """Validate an untrusted text input."""
    return SecurityInputValidator(config).validate(value)


def validate_security_url(
    url: str,
    config: SecurityValidationConfig | None = None,
) -> SecurityValidationResult:
    """Validate a URL."""
    return SecurityInputValidator(config).validate_url(url)
