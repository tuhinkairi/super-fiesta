"""
Security provider interfaces.

Defines contracts for security validation and input sanitization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class SecurityProvider(ABC):
    """Base contract for security-related providers."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the security provider is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None


class InputSanitizer(SecurityProvider):
    """Interface for sanitizing untrusted input."""

    @abstractmethod
    def sanitize(self, value: str) -> str:
        """Return a sanitized representation of the input."""
        raise NotImplementedError


class AccessControlProvider(SecurityProvider):
    """Interface for authorization and permission checks."""

    @abstractmethod
    def authorize(
        self,
        principal: str,
        action: str,
        resource: str,
        context: Mapping[str, Any] | None = None,
    ) -> bool:
        """Determine whether a principal may perform an action."""
        raise NotImplementedError


class SecurityValidator(SecurityProvider):
    """Interface for validating data against security rules."""

    @abstractmethod
    def validate(
        self,
        value: Any,
        context: Mapping[str, Any] | None = None,
    ) -> bool:
        """Return whether the supplied value passes security checks."""
        raise NotImplementedError
