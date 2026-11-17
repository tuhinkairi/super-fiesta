"""Health monitoring utilities for vector databases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.database.base import BaseVectorDatabase

logger = get_logger(__name__)


@dataclass
class DatabaseHealth:
    """Represents the health status of a vector database."""

    provider: str
    healthy: bool
    checked_at: datetime
    message: str = ""

    @property
    def status(self) -> str:
        return "healthy" if self.healthy else "unhealthy"


class DatabaseHealthChecker:
    """Check and report vector database health."""

    def __init__(
        self,
        database: BaseVectorDatabase,
        provider_name: str = "vector_database",
    ) -> None:
        if database is None:
            raise ValueError("A database instance is required.")

        self.database = database
        self.provider_name = provider_name

    def check(self) -> DatabaseHealth:
        """Perform a database health check."""
        checked_at = datetime.now(timezone.utc)

        try:
            healthy = self.database.health_check()

            if healthy:
                message = "Database is operational."
            else:
                message = "Database health check returned False."

            return DatabaseHealth(
                provider=self.provider_name,
                healthy=healthy,
                checked_at=checked_at,
                message=message,
            )

        except Exception as exc:
            logger.exception("Database health check failed.")

            return DatabaseHealth(
                provider=self.provider_name,
                healthy=False,
                checked_at=checked_at,
                message=str(exc),
            )

    def is_healthy(self) -> bool:
        """Return only the health status."""
        return self.check().healthy
