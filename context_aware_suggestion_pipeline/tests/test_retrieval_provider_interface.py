
from context_aware_suggestion_rag.interfaces.retrieval_provider import (
    RetrievalProvider,
)
from context_aware_suggestion_rag.retrieval.models import (
    RetrievalQuery,
    RetrievalResult,
)


class FakeRetrievalProvider(RetrievalProvider):

    def retrieve(self, query):
        return RetrievalResult(
            query=query.query,
            documents=[],
            retrieval_method="fake",
        )

    def health_check(self):
        return True


def main():
    provider = FakeRetrievalProvider()

    assert isinstance(provider, RetrievalProvider)
    print("Retrieval provider inheritance: PASS")

    assert provider.health_check()
    print("Retrieval provider health check: PASS")

    query = RetrievalQuery(query="Explain RAG")

    result = provider.retrieve(query)

    assert isinstance(result, RetrievalResult)
    assert result.retrieval_method == "fake"
    print("Single retrieval interface: PASS")

    queries = [
        RetrievalQuery(query="Explain AI"),
        RetrievalQuery(query="Explain ML"),
    ]

    results = provider.retrieve_many(queries)

    assert len(results) == 2
    assert all(isinstance(item, RetrievalResult) for item in results)
    print("Batch retrieval interface: PASS")

    try:
        provider.retrieve_many(["invalid"])
    except TypeError:
        pass
    else:
        raise AssertionError("Invalid query sequence was accepted")

    print("Batch input validation: PASS")

    provider.close()
    print("Provider close interface: PASS")

    print("\nAll retrieval provider interface tests passed.")


if __name__ == "__main__":
    main()
