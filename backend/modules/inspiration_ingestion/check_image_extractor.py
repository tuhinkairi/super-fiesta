from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from modules.inspiration_ingestion.extractors.image_extractor import (
    ImageExtractor,
)


def main():
    with TemporaryDirectory() as temp_dir:
        image_path = Path(temp_dir) / "sample.png"

        # Generate a sample image for testing.
        sample_image = Image.new(
            "RGB",
            (800, 600),
            color="blue",
        )
        sample_image.save(image_path)

        extractor = ImageExtractor()
        result = extractor.extract_metadata(image_path)

        print("Image extraction successful!")
        print("File name:", result["file_name"])
        print("Format:", result["format"])
        print("Dimensions:", result["width"], "x", result["height"])
        print("Color mode:", result["mode"])
        print("File size:", result["file_size_bytes"], "bytes")

        # Verify extracted metadata.
        assert result["format"] == "PNG"
        assert result["width"] == 800
        assert result["height"] == 600
        assert result["mode"] == "RGB"

        # Test invalid image.
        invalid_path = Path(temp_dir) / "invalid.png"
        invalid_path.write_text("This is not an image.")

        try:
            extractor.extract_metadata(invalid_path)
            raise AssertionError("Invalid image was accepted!")
        except ValueError as error:
            print("\nInvalid image correctly rejected:", error)

        print("\nAll Image Extractor checks passed!")


if __name__ == "__main__":
    main()
