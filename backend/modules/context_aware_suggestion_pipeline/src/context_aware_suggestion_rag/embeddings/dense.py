"""Google Gemini dense embedding provider."""

from collections.abc import Sequence
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.embedding_config import (
    get_embedding_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.llm_config import get_llm_config
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.base import (
    BaseDenseEmbeddingProvider,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.models import DenseEmbedding
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import EmbeddingError

logger = get_logger(__name__)


class GoogleDenseEmbeddingProvider(BaseDenseEmbeddingProvider):
    """Generate dense embeddings through Google's GenAI SDK."""

    def __init__(self) -> None:
        self.embedding_config = get_embedding_config()
        self.llm_config = get_llm_config()
        self._client: Any | None = None
        self._connected = False

        self.model = self.embedding_config.dense_model
        self.dimension = self.embedding_config.dense_dimension

    def connect(self) -> None:
        """Initialize the Google GenAI client."""
        if self._connected:
            return

        api_key = self.llm_config.api_key.get_secret_value()

        if not api_key:
            raise EmbeddingError(
                "GEMINI_API_KEY is not configured."
            )

        try:
            from google import genai

            self._client = genai.Client(api_key=api_key)
            self._connected = True

            logger.info("Google dense embedding provider connected.")

        except Exception as exc:
            raise EmbeddingError(
                f"Could not connect to Google GenAI: {exc}"
            ) from exc

    def health_check(self) -> bool:
        """Check whether the provider has been initialized."""
        try:
            self.connect()
            return self._client is not None
        except EmbeddingError:
            return False

    def embed_text(self, text: str) -> DenseEmbedding:
        """Generate an embedding for a single text."""
        results = self.embed_texts([text])
        return results[0]

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[DenseEmbedding]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("All input texts must be non-empty strings.")

        self.connect()

        try:
            response = self._client.models.embed_content(
                model=self.model,
                contents=list(texts),
                config={
                    "output_dimensionality": self.dimension,
                },
            )

            embeddings = getattr(response, "embeddings", None)

            if not embeddings or len(embeddings) != len(texts):
                raise EmbeddingError(
                    "Google returned an unexpected number of embeddings."
                )

            results: list[DenseEmbedding] = []

            for item in embeddings:
                values = getattr(item, "values", None)

                if values is None:
                    raise EmbeddingError(
                        "Google returned an embedding without vector values."
                    )

                embedding = DenseEmbedding(
                    values=list(values),
                    model=self.model,
                )

                if embedding.dimension != self.dimension:
                    raise EmbeddingError(
                        "Embedding dimension mismatch: "
                        f"expected {self.dimension}, "
                        f"received {embedding.dimension}."
                    )

                results.append(embedding)

            return results

        except EmbeddingError:
            raise
        except Exception as exc:
            raise EmbeddingError(
                f"Google embedding generation failed: {exc}"
            ) from exc

    def get_dimension(self) -> int:
        """Return the configured embedding dimension."""
        return self.dimension
