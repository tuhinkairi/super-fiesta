"""Local BM25-style sparse embedding provider."""

import hashlib
import re
from collections import Counter
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.base import (
    BaseSparseEmbeddingProvider,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.models import SparseEmbedding

logger = get_logger(__name__)


class BM25SparseEmbeddingProvider(BaseSparseEmbeddingProvider):
    """Generate deterministic, hashed sparse vectors using BM25-style weights.

    This lightweight implementation uses term frequency and document-length
    normalization. It does not calculate corpus-wide inverse document frequency.
    """

    def __init__(
        self,
        hash_space_size: int = 1_000_000,
        k1: float = 1.5,
        b: float = 0.75,
        average_document_length: float = 100.0,
    ) -> None:
        if hash_space_size <= 0:
            raise ValueError("Hash space size must be positive.")

        if k1 <= 0:
            raise ValueError("k1 must be positive.")

        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1.")

        if average_document_length <= 0:
            raise ValueError("Average document length must be positive.")

        self.hash_space_size = hash_space_size
        self.k1 = k1
        self.b = b
        self.average_document_length = average_document_length
        self.model = "local-bm25-hash-v1"

    def connect(self) -> None:
        """Initialize the local provider.

        No external connection is required.
        """
        logger.debug("Local BM25 sparse provider is ready.")

    def health_check(self) -> bool:
        """Check whether the provider is ready."""
        return self.hash_space_size > 0

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Convert text into lowercase alphanumeric tokens."""
        return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    def _token_to_index(self, token: str) -> int:
        """Convert a token into a deterministic sparse vector index."""
        digest = hashlib.blake2b(
            token.encode("utf-8"),
            digest_size=8,
        ).digest()

        return int.from_bytes(digest, byteorder="big") % self.hash_space_size

    def embed_text(self, text: str) -> SparseEmbedding:
        """Generate a sparse embedding for one text."""
        results = self.embed_texts([text])
        return results[0]

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[SparseEmbedding]:
        """Generate sparse embeddings for multiple texts."""
        if not texts:
            return []

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("All input texts must be non-empty strings.")

        self.connect()
        results: list[SparseEmbedding] = []

        for text in texts:
            tokens = self._tokenize(text)

            if not tokens:
                raise ValueError(
                    "Text must contain at least one alphanumeric token."
                )

            frequencies = Counter(tokens)
            document_length = len(tokens)

            # Aggregate weights in case two tokens share a hash index.
            index_weights: dict[int, float] = {}

            for token, frequency in frequencies.items():
                index = self._token_to_index(token)

                numerator = frequency * (self.k1 + 1)
                denominator = frequency + self.k1 * (
                    1 - self.b
                    + self.b * (
                        document_length / self.average_document_length
                    )
                )

                weight = numerator / denominator
                index_weights[index] = index_weights.get(index, 0.0) + weight

            sorted_items = sorted(index_weights.items())

            results.append(
                SparseEmbedding(
                    indices=[index for index, _ in sorted_items],
                    values=[weight for _, weight in sorted_items],
                    model=self.model,
                )
            )

        return results
