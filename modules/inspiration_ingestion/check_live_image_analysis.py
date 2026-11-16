
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from modules.inspiration_ingestion.processing.image_analyzer import (
    ImageAnalyzer,
)


def create_sample_image(image_path: Path):
    """Create a simple visual composition for Gemini to analyze."""

    image = Image.new("RGB", (800, 600), color="#F2EBDD")
    draw = ImageDraw.Draw(image)

    # Draw a blue central circle.
    draw.ellipse(
        (250, 150, 550, 450),
        fill="#2878B5",
    )

    # Draw a yellow rectangle.
    draw.rectangle(
        (80, 100, 220, 300),
        fill="#F4C542",
    )

    # Draw a green horizontal rectangle.
    draw.rectangle(
        (580, 350, 740, 480),
        fill="#4D9B72",
    )

    image.save(image_path)


def main():
    analyzer = None

    try:
        with TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "live_sample.png"

            print("Creating sample image...")
            create_sample_image(image_path)

            print("Image created:", image_path.name)

            # Initialize the real Gemini-backed analyzer.
            analyzer = ImageAnalyzer()

            print("\nSending image to Gemini...")
            result = analyzer.analyze_image(image_path)

            print("\nIMAGE ANALYSIS RESULT")
            print("=====================")

            print("\nSummary:")
            print(result.summary)

            print("\nDescription:")
            print(result.description)

            print("\nKeywords:")
            print(result.keywords)

            print("\nThemes:")
            print(result.themes)

            print("\nMood tags:")
            print(result.mood_tags)

            # Validate the structured response.
            assert result.summary.strip()
            assert result.description.strip()
            assert result.keywords
            assert result.themes
            assert result.mood_tags

            print("\nPASS: Gemini returned structured image analysis.")
            print("PASS: All required fields are populated.")

            print("\n====================================")
            print("LIVE IMAGE ANALYSIS TEST PASSED")
            print("====================================")
            print("Expected Gemini requests: 1")
            print("Image analysis: 1")
            print("Embedding generation: 0")

    finally:
        if analyzer is not None:
            analyzer.close()


if __name__ == "__main__":
    main()
