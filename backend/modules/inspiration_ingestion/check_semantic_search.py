from tempfile import TemporaryDirectory
from pathlib import Path

from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)

from modules.inspiration_ingestion.processing.search_engine import (
    SemanticSearchEngine,
)

from modules.inspiration_ingestion.types import InspirationRecord


# Fake embedding generator.
class FakeEmbeddingGenerator:

    def generate(self, text):
        # The query points in the first dimension.
        return [1.0] + [0.0] * 767


def make_embedding(first, second):
    return [first, second] + [0.0] * 766


def main():

    with TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "search_test.db"

        store = MetadataStore(db_path=db_path)

        # Record 1: Highly relevant.
        relevant = InspirationRecord(
            file_name="space_story.txt",
            content_type="text",
            summary="An astronaut explores a distant planet.",
            description="A science fiction space adventure.",
            embedding=make_embedding(1.0, 0.0),
        )

        # Record 2: Unrelated.
        unrelated = InspirationRecord(
            file_name="ocean_story.txt",
            content_type="text",
            summary="A diver explores the ocean.",
            description="An underwater adventure.",
            embedding=make_embedding(0.0, 1.0),
        )

        # Record 3: Opposite direction.
        opposite = InspirationRecord(
            file_name="opposite_story.txt",
            content_type="text",
            summary="A completely different concept.",
            description="An opposite semantic direction.",
            embedding=make_embedding(-1.0, 0.0),
        )

        store.save(relevant)
        store.save(unrelated)
        store.save(opposite)

        print("Three test records saved.")

        # Initialize the search engine.
        engine = SemanticSearchEngine(
            metadata_store=store,
            embedding_generator=FakeEmbeddingGenerator(),
        )

        # Search.
        results = engine.search(
            "A story about space exploration",
            top_k=3,
        )

        assert len(results) == 3

        print("\nSearch ranking:")

        for index, result in enumerate(results, start=1):
            record = result["record"]
            score = result["similarity"]

            print(f"{index}. {record.file_name} " f"| Similarity: {score:.2f}")

        # Verify ranking.
        assert results[0]["record"].id == relevant.id
        assert results[1]["record"].id == unrelated.id
        assert results[2]["record"].id == opposite.id

        print("\nRanking verification passed.")

        # Verify top_k.
        top_result = engine.search(
            "space exploration",
            top_k=1,
        )

        assert len(top_result) == 1
        assert top_result[0]["record"].id == relevant.id

        print("Top-k verification passed.")

        # Verify empty query rejection.
        try:
            engine.search("   ")
            raise AssertionError("Empty query was accepted.")
        except ValueError:
            print("Empty query validation passed.")

        # Verify invalid top_k rejection.
        try:
            engine.search("space", top_k=0)
            raise AssertionError("Invalid top_k was accepted.")
        except ValueError:
            print("Invalid top-k validation passed.")

    print("\nAll semantic search checks passed!")


if __name__ == "__main__":
    main()
