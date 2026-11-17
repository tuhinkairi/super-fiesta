
from context_aware_suggestion_rag.interfaces.reranker_provider import (
    RerankerProvider,
)
from context_aware_suggestion_rag.retrieval.models import RetrievedDocument


class FakeRerankerProvider(RerankerProvider):
    def connect(self) -> None:
        self.connected = True

    def health_check(self) -> bool:
        return True

    def rerank(
        self,
        query: str,
        documents: list[RetrievedDocument],
        top_k: int,
    ) -> list[RetrievedDocument]:
        return sorted(
            documents,
            key=lambda document: document.score,
            reverse=True,
        )[:top_k]


provider = FakeRerankerProvider()

provider.connect()
assert provider.connected is True
print("Reranker provider connection: PASS")

assert provider.health_check() is True
print("Reranker provider health check: PASS")

documents = [
    RetrievedDocument(
        id="doc-1",
        content="First document",
        score=0.6,
        metadata={},
        namespace="documents",
        source_type="document",
        rank=1,
    ),
    RetrievedDocument(
        id="doc-2",
        content="Second document",
        score=0.9,
        metadata={},
        namespace="documents",
        source_type="document",
        rank=2,
    ),
]

results = provider.rerank("test query", documents, 1)

assert len(results) == 1
assert results[0].id == "doc-2"
print("Document reranking: PASS")

assert RerankerProvider.__abstractmethods__ == {
    "connect",
    "health_check",
    "rerank",
}
print("Reranker provider abstract methods: PASS")

provider.close()
print("Reranker provider tests passed.")
