
from modules.inspiration_ingestion.processing.embedding_generator import (
    EmbeddingGenerator,
)


class FakeLLMClient:

    def __init__(self, dimensions=768):
        self.dimensions = dimensions

    def generate_embedding(self, text):
        return [0.01] * self.dimensions


def main():

    # Test successful embedding generation.
    fake_client = FakeLLMClient(dimensions=768)

    generator = EmbeddingGenerator(
        llm_client=fake_client
    )

    result = generator.generate(
        "A lonely astronaut searching for home."
    )

    print("Embedding generated successfully!")
    print("Vector dimensions:", len(result))

    assert len(result) == 768
    assert all(isinstance(value, float) for value in result)

    # Test incorrect vector dimensions.
    incorrect_client = FakeLLMClient(dimensions=128)

    incorrect_generator = EmbeddingGenerator(
        llm_client=incorrect_client
    )

    try:
        incorrect_generator.generate("Sample text")

        raise AssertionError(
            "Incorrect dimensions should have been rejected."
        )

    except ValueError as error:
        print("\nIncorrect dimensions correctly rejected:")
        print(error)

    # Test empty input.
    try:
        generator.generate("")

        raise AssertionError(
            "Empty text should have been rejected."
        )

    except ValueError as error:
        print("\nEmpty input correctly rejected:")
        print(error)

    print("\nAll Embedding Generator checks passed!")


if __name__ == "__main__":
    main()
