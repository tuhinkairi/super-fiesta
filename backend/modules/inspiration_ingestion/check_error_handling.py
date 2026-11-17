from pathlib import Path
from tempfile import TemporaryDirectory

from modules.inspiration_ingestion.ingestion.file_handler import (
    FileHandler,
)

from modules.inspiration_ingestion.extractors.pdf_extractor import (
    PDFExtractor,
)

from modules.inspiration_ingestion.extractors.image_extractor import (
    ImageExtractor,
)

from modules.inspiration_ingestion.extractors.text_extractor import (
    TextExtractor,
)

from modules.inspiration_ingestion.extractors.url_extractor import (
    URLExtractor,
)

from modules.inspiration_ingestion.pipeline.ingestion_pipeline import (
    InspirationIngestionPipeline,
)


class FakeLLMClient:
    """Prevents real Gemini API calls."""

    def generate_structured(self, prompt, response_schema):
        raise AssertionError("Gemini should not be called in this test.")

    def generate_image_structured(self, prompt, image_path, response_schema):
        raise AssertionError("Gemini should not be called in this test.")

    def generate_embedding(self, text):
        raise AssertionError("Gemini should not be called in this test.")


class FakeMetadataStore:

    def save(self, record):
        pass


def expect_error(description, expected_error, function):

    try:
        function()
    except expected_error as error:
        print(f"{description} passed: {error}")
    else:
        raise AssertionError(
            f"{description} failed: expected {expected_error.__name__}"
        )


def main():

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        file_handler = FileHandler()
        pdf_extractor = PDFExtractor()
        image_extractor = ImageExtractor()
        text_extractor = TextExtractor()
        url_extractor = URLExtractor()

        # 1. Unsupported file extension.
        unsupported_file = temp_path / "malware.exe"
        unsupported_file.write_text("sample", encoding="utf-8")

        expect_error(
            "Unsupported file validation",
            ValueError,
            lambda: file_handler.validate_file(unsupported_file),
        )

        # 2. Corrupted PDF.
        corrupted_pdf = temp_path / "broken.pdf"
        corrupted_pdf.write_text(
            "This is not a real PDF.",
            encoding="utf-8",
        )

        expect_error(
            "Corrupted PDF validation",
            RuntimeError,
            lambda: pdf_extractor.extract_text(corrupted_pdf),
        )

        # 3. Corrupted image.
        corrupted_image = temp_path / "broken.png"
        corrupted_image.write_text(
            "This is not a real image.",
            encoding="utf-8",
        )

        expect_error(
            "Corrupted image validation",
            ValueError,
            lambda: image_extractor.extract_metadata(corrupted_image),
        )

        # 4. Empty text file.
        empty_text = temp_path / "empty.txt"
        empty_text.write_text("", encoding="utf-8")

        extraction = text_extractor.extract_text(empty_text)

        assert extraction["text"] == ""
        assert extraction["word_count"] == 0

        pipeline = InspirationIngestionPipeline(
            llm_client=FakeLLMClient(),
            metadata_store=FakeMetadataStore(),
        )

        pipeline.file_handler.originals_dir = temp_path / "originals"

        expect_error(
            "Empty text ingestion validation",
            ValueError,
            lambda: pipeline.ingest_file(empty_text),
        )

        # 5. Invalid URL schemes.
        expect_error(
            "Invalid URL scheme validation",
            ValueError,
            lambda: url_extractor.extract_content("ftp://example.com/article"),
        )

        expect_error(
            "Invalid URL format validation",
            ValueError,
            lambda: url_extractor.extract_content("not-a-valid-url"),
        )

    print("\nAll error-handling checks passed!")


if __name__ == "__main__":
    main()
