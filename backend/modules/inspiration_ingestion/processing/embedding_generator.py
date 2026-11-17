from modules.story_intelligence.llm.llm_client import LLMClient


class EmbeddingGenerator:
    """
    Generates semantic embeddings for inspiration content.
    """

    EXPECTED_DIMENSIONS = 768

    def __init__(self, llm_client=None):
        self._owns_client = llm_client is None
        self.llm_client = llm_client or LLMClient()

    def generate(self, text: str) -> list[float]:
        """
        Generate a 768-dimensional embedding for text.
        """

        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")

        embedding = self.llm_client.generate_embedding(text)

        if len(embedding) != self.EXPECTED_DIMENSIONS:
            raise ValueError(
                f"Expected {self.EXPECTED_DIMENSIONS} dimensions, "
                f"but received {len(embedding)}."
            )

        return embedding

    def close(self):
        """
        Close the LLM client only if this generator created it.
        """

        if self._owns_client:
            self.llm_client.close()
