"""
Recommendation provider interfaces.

Defines contracts for recommendation generation and selection.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)


class RecommendationProvider(ABC):
    """Abstract contract for recommendation providers."""

    @abstractmethod
    def generate(
        self,
        candidates: Sequence[Any],
    ) -> list[Recommendation]:
        """Generate recommendations from candidate data."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError

    def configure(
        self,
        settings: Mapping[str, Any],
    ) -> None:
        """Apply optional provider settings."""
        return None

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
