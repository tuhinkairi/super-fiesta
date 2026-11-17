from modules.inspiration_ingestion.types import InspirationRecord

from modules.inspiration_ingestion.processing.search_engine import (
    SemanticSearchEngine,
)


# Mock database.
class FakeMetadataStore:

    def get_all(self):

        return [
            InspirationRecord(
                file_name="astronaut.txt",
                content_type="text",
                summary="A lonely astronaut searching for home.",
                embedding=[0.8, 0.6, 0.0],
            ),
            InspirationRecord(
                file_name="village.txt",
                content_type="text",
                summary="A peaceful village surrounded by nature.",
                embedding=[0.0, 1.0, 0.0],
            ),
            InspirationRecord(
                file_name="betrayal.txt",
                content_type="text",
                summary="Two friends betray each other.",
                embedding=[-1.0, 0.0, 0.0],
            ),
            InspirationRecord(
                file_name="no_embedding.txt",
                content_type="text",
                summary="This record has no embedding.",
                embedding=None,
            ),
        ]


# Mock embedding generator.
class FakeEmbeddingGenerator:

    def generate(self, text):
        return [1.0, 0.0, 0.0]


def main():

    engine = SemanticSearchEngine(
        metadata_store=FakeMetadataStore(),
        embedding_generator=FakeEmbeddingGenerator(),
    )

    # Test cosine similarity.
    similarity = engine.cosine_similarity(
        [1.0, 0.0, 0.0],
        [0.8, 0.6, 0.0],
    )

    print("Cosine similarity:", similarity)

    assert abs(similarity - 0.8) < 0.0001

    # Test semantic search ranking.
    results = engine.search(
        query="Find something about isolation.",
        top_k=3,
    )

    print("\nSearch results:")

    for index, result in enumerate(results, start=1):

        record = result["record"]

        print(f"\n{index}. {record.file_name}")
        print("Summary:", record.summary)
        print("Similarity:", round(result["similarity"], 4))

    # Verify ranking.
    assert len(results) == 3

    assert results[0]["record"].file_name == "astronaut.txt"
    assert results[1]["record"].file_name == "village.txt"
    assert results[2]["record"].file_name == "betrayal.txt"

    # Test top_k.
    top_result = engine.search(
        query="Find something about isolation.",
        top_k=1,
    )

    assert len(top_result) == 1

    print("\nTop-k filtering passed.")

    # Test empty query.
    try:
        engine.search("")

        raise AssertionError("Empty query should have been rejected.")

    except ValueError as error:
        print("Empty query correctly rejected:", error)

    # Test invalid top_k.
    try:
        engine.search("sample query", top_k=0)

        raise AssertionError("Invalid top_k should have been rejected.")

    except ValueError as error:
        print("Invalid top_k correctly rejected:", error)

    # Test mismatched vector dimensions.
    try:
        engine.cosine_similarity(
            [1.0, 0.0],
            [1.0, 0.0, 0.0],
        )

        raise AssertionError("Mismatched dimensions should have been rejected.")

    except ValueError as error:
        print("Dimension mismatch correctly rejected:", error)

    # Test zero vectors.
    zero_similarity = engine.cosine_similarity(
        [0.0, 0.0],
        [1.0, 0.0],
    )

    assert zero_similarity == 0.0

    print("\nZero-vector handling passed.")

    print("\nAll Semantic Search Engine checks passed!")


if __name__ == "__main__":
    main()
