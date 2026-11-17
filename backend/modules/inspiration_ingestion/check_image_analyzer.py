from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from modules.inspiration_ingestion.processing.image_analyzer import (
    ImageAnalyzer,
)

from modules.inspiration_ingestion.processing.analyzer import (
    InspirationAnalysis,
)


class FakeLLMClient:

    def __init__(self):
        self.received_prompt = ""
        self.received_image_path = None

    def generate_image_structured(
        self,
        prompt,
        image_path,
        response_schema,
    ):
        self.received_prompt = prompt
        self.received_image_path = Path(image_path)

        return response_schema(
            summary="A blue abstract square.",
            description=(
                "A simple blue square image with " "a clean and minimal appearance."
            ),
            keywords=[
                "blue",
                "square",
                "minimal",
                "abstract",
                "simple",
            ],
            themes=[
                "Minimalism",
                "Simplicity",
            ],
            mood_tags=[
                "Calm",
                "Peaceful",
            ],
        )


def main():

    with TemporaryDirectory() as temp_dir:

        # Create a sample image for testing.
        image_path = Path(temp_dir) / "sample.png"

        image = Image.new(
            "RGB",
            (800, 600),
            color="blue",
        )

        image.save(image_path)

        fake_client = FakeLLMClient()

        analyzer = ImageAnalyzer(llm_client=fake_client)

        result = analyzer.analyze_image(image_path)

        print("Image analysis completed successfully!")

        print("\nSummary:")
        print(result.summary)

        print("\nDescription:")
        print(result.description)

        print("\nKeywords:")
        print(result.keywords)

        print("\nThemes:")
        print(result.themes)

        print("\nMood Tags:")
        print(result.mood_tags)

        # Verify the structured response.
        assert isinstance(result, InspirationAnalysis)

        assert result.summary
        assert result.description
        assert result.keywords
        assert result.themes
        assert result.mood_tags

        # Verify the image was passed to the fake client.
        assert fake_client.received_image_path == image_path

        # Verify image metadata was included in the prompt.
        assert "800 x 600" in fake_client.received_prompt

        print("\nImage metadata correctly included in prompt.")

        # Verify missing images are rejected.
        try:
            analyzer.analyze_image(Path(temp_dir) / "missing.png")

            raise AssertionError("Missing image should have been rejected.")

        except FileNotFoundError:
            print("Missing image correctly rejected.")

    print("\nAll Image Analyzer checks passed!")


if __name__ == "__main__":
    main()
