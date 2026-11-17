"""
Notification provider interfaces.

Defines a provider-independent contract for sending notifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class NotificationProvider(ABC):
    """Abstract contract for notification providers."""

    @abstractmethod
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> bool:
        """Send a notification to a recipient."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the notification provider is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
