
from context_aware_suggestion_rag.interfaces.embedding_provider import (
    DenseEmbeddingProvider,
    EmbeddingProvider,
    SparseEmbeddingProvider,
)
from context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)


class FakeDenseProvider(DenseEmbeddingProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def embed_text(self, text):
        return DenseEmbedding(
            values=[0.1, 0.2, 0.3],
            model="fake-dense",
        )

    def embed_texts(self, texts):
        return [self.embed_text(text) for text in texts]

    def get_dimension(self):
        return 3


class FakeSparseProvider(SparseEmbeddingProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def embed_text(self, text):
        return SparseEmbedding(
            indices=[1, 3],
            values=[0.5, 0.8],
            model="fake-sparse",
        )

    def embed_texts(self, texts):
        return [self.embed_text(text) for text in texts]


def main():
    dense = FakeDenseProvider()
    sparse = FakeSparseProvider()

    assert isinstance(dense, EmbeddingProvider)
    assert isinstance(sparse, EmbeddingProvider)
    print("Embedding provider inheritance: PASS")

    assert dense.health_check()
    assert sparse.health_check()
    print("Provider health checks: PASS")

    dense_result = dense.embed_text("test")
    assert isinstance(dense_result, DenseEmbedding)
    assert dense.get_dimension() == 3
    print("Dense embedding interface: PASS")

    sparse_result = sparse.embed_text("test")
    assert isinstance(sparse_result, SparseEmbedding)
    print("Sparse embedding interface: PASS")

    assert len(dense.embed_texts(["one", "two"])) == 2
    assert len(sparse.embed_texts(["one", "two"])) == 2
    print("Batch embedding interfaces: PASS")

    print("\nAll embedding provider interface tests passed.")


if __name__ == "__main__":
    main()
