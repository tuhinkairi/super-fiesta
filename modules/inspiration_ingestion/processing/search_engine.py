
import math

from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)

from modules.inspiration_ingestion.processing.embedding_generator import (
    EmbeddingGenerator,
)


class SemanticSearchEngine:
    """
    Finds relevant inspiration using embedding similarity.
    """

    def __init__(self, metadata_store=None, embedding_generator=None):

        self.metadata_store = metadata_store or MetadataStore()

        self._owns_generator = embedding_generator is None

        self.embedding_generator = (
            embedding_generator or EmbeddingGenerator()
        )

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Embedding dimensions must match."
            )

        magnitude_a = math.sqrt(
            sum(value * value for value in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(value * value for value in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        return dot_product / (magnitude_a * magnitude_b)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        # Generate an embedding for the user's search query.
        query_embedding = self.embedding_generator.generate(
            query
        )

        # Retrieve all saved inspiration records.
        records = self.metadata_store.get_all()

        results = []

        for record in records:

            # Ignore records that do not have embeddings yet.
            if not record.embedding:
                continue

            similarity = self.cosine_similarity(
                query_embedding,
                record.embedding,
            )

            results.append({
                "record": record,
                "similarity": similarity,
            })

        # Highest similarity first.
        results.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        return results[:top_k]

    def close(self):
        """
        Close resources owned by this search engine.
        """

        if self._owns_generator:
            self.embedding_generator.close()
