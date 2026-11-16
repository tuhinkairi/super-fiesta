
from pathlib import Path
from tempfile import TemporaryDirectory

from modules.inspiration_ingestion.extractors.text_extractor import (
    TextExtractor,
)


def main():
    with TemporaryDirectory() as temp_dir:
        sample_file = Path(temp_dir) / "story.md"

        sample_content = (
            "# A New Beginning\n"
            "Two friends discover a mysterious world."
        )

        sample_file.write_text(
            sample_content,
            encoding="utf-8",
        )

        extractor = TextExtractor()
        result = extractor.extract_text(sample_file)

        print("Text extraction successful!")
        print("File name:", result["file_name"])
        print("Extracted text:", result["text"])
        print("Character count:", result["character_count"])
        print("Word count:", result["word_count"])

        assert result["file_name"] == "story.md"
        assert "mysterious world" in result["text"]
        assert result["word_count"] == 10

        # Test unsupported extension.
        invalid_file = Path(temp_dir) / "sample.exe"
        invalid_file.write_text("Invalid file")

        try:
            extractor.extract_text(invalid_file)
            raise AssertionError("Unsupported file was accepted!")
        except ValueError as error:
            print("\nInvalid file correctly rejected:", error)

        print("\nAll Text Extractor checks passed!")


if __name__ == "__main__":
    main()
