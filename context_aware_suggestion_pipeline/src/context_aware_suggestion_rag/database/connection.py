"""Pinecone connection management."""

from typing import Any

from context_aware_suggestion_rag.config.pinecone_config import (
    get_pinecone_config,
)
from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.exceptions import (
    ConfigurationError,
    PineconeConnectionError,
)

logger = get_logger(__name__)


class PineconeConnection:
    """Manage Pinecone client and index connections."""

    def __init__(self) -> None:
        self.config = get_pinecone_config()
        self._client: Any | None = None
        self._index: Any | None = None
        self._connected = False

    def connect(self) -> Any:
        """Initialize and return the Pinecone client."""
        if self._connected and self._client is not None:
            return self._client

        api_key = self.config.api_key.get_secret_value()

        if not api_key:
            raise ConfigurationError(
                "PINECONE_API_KEY is not configured."
            )

        try:
            from pinecone import Pinecone

            self._client = Pinecone(api_key=api_key)
            self._connected = True

            logger.info("Connected to Pinecone.")
            return self._client

        except Exception as exc:
            self._connected = False
            self._client = None

            raise PineconeConnectionError(
                f"Failed to connect to Pinecone: {exc}"
            ) from exc

    def get_client(self) -> Any:
        """Return the active Pinecone client."""
        return self.connect()

    def get_index(self, index_name: str | None = None) -> Any:
        """Return a Pinecone index handle."""
        client = self.connect()
        name = index_name or self.config.index_name

        if not name or not name.strip():
            raise ConfigurationError(
                "Pinecone index name cannot be empty."
            )

        try:
            self._index = client.Index(name)
            return self._index

        except Exception as exc:
            raise PineconeConnectionError(
                f"Could not access Pinecone index '{name}': {exc}"
            ) from exc

    def health_check(self) -> bool:
        """Check whether Pinecone is reachable."""
        try:
            client = self.connect()
            client.list_indexes()
            return True

        except Exception:
            logger.exception("Pinecone health check failed.")
            return False

    def close(self) -> None:
        """Release local connection references."""
        self._index = None
        self._client = None
        self._connected = False

        logger.info("Pinecone connection references released.")
