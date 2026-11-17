"""Pinecone index lifecycle and configuration management."""

from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.pinecone_config import (
    get_pinecone_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.connection import (
    PineconeConnection,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import (
    IndexConfigurationError,
    PineconeConnectionError,
)

logger = get_logger(__name__)


class PineconeIndexManager:
    """Create, inspect, and validate a Pinecone index."""

    def __init__(
        self,
        connection: PineconeConnection | None = None,
    ) -> None:
        self.config = get_pinecone_config()
        self.connection = connection or PineconeConnection()

    def _list_index_names(self) -> set[str]:
        """Return the names of available Pinecone indexes."""
        client = self.connection.get_client()

        try:
            response = client.list_indexes()
            indexes = getattr(response, "indexes", None)

            if indexes is None and isinstance(response, dict):
                indexes = response.get("indexes", [])

            names: set[str] = set()

            for index in indexes or []:
                if isinstance(index, dict):
                    name = index.get("name")
                else:
                    name = getattr(index, "name", None)

                if name:
                    names.add(name)

            return names

        except Exception as exc:
            raise PineconeConnectionError(
                f"Failed to list Pinecone indexes: {exc}"
            ) from exc

    def index_exists(self) -> bool:
        """Check whether the configured index exists."""
        return self.config.index_name in self._list_index_names()

    def create_index(self) -> None:
        """Create the configured index if it does not already exist."""
        if self.index_exists():
            logger.info(
                "Pinecone index '%s' already exists.",
                self.config.index_name,
            )
            return

        if not self.config.create_index_if_missing:
            raise IndexConfigurationError(
                f"Index '{self.config.index_name}' does not exist "
                "and automatic creation is disabled."
            )

        client = self.connection.get_client()

        try:
            from pinecone import ServerlessSpec

            client.create_index(
                name=self.config.index_name,
                dimension=self.config.dimension,
                metric=self.config.metric,
                spec=ServerlessSpec(
                    cloud=self.config.cloud,
                    region=self.config.region,
                ),
                deletion_protection=self.config.deletion_protection,
            )

            logger.info(
                "Created Pinecone index '%s'.",
                self.config.index_name,
            )

        except Exception as exc:
            raise IndexConfigurationError(
                f"Failed to create Pinecone index: {exc}"
            ) from exc

    def describe_index(self) -> dict[str, Any]:
        """Return details about the configured index."""
        if not self.index_exists():
            raise IndexConfigurationError(
                f"Index '{self.config.index_name}' does not exist."
            )

        client = self.connection.get_client()

        try:
            description = client.describe_index(
                self.config.index_name
            )

            if hasattr(description, "to_dict"):
                return description.to_dict()

            if isinstance(description, dict):
                return description

            return {
                "name": getattr(description, "name", None),
                "dimension": getattr(description, "dimension", None),
                "metric": getattr(description, "metric", None),
                "status": getattr(description, "status", None),
            }

        except Exception as exc:
            raise PineconeConnectionError(
                f"Failed to describe Pinecone index: {exc}"
            ) from exc

    def validate_index(self) -> bool:
        """Validate the index dimension and metric."""
        details = self.describe_index()

        actual_dimension = details.get("dimension")
        actual_metric = details.get("metric")

        if actual_dimension != self.config.dimension:
            raise IndexConfigurationError(
                f"Dimension mismatch: configured "
                f"{self.config.dimension}, actual {actual_dimension}."
            )

        if actual_metric != self.config.metric:
            raise IndexConfigurationError(
                f"Metric mismatch: configured "
                f"{self.config.metric}, actual {actual_metric}."
            )

        logger.info("Pinecone index configuration validated.")
        return True

    def ensure_index(self) -> bool:
        """Create the index if needed, then validate it."""
        self.create_index()
        return self.validate_index()
