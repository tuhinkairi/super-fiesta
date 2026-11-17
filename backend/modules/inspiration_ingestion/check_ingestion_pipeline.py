from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf
from PIL import Image

from modules.inspiration_ingestion.pipeline.ingestion_pipeline import (
    InspirationIngestionPipeline,
)


# Fake Gemini client: no real API requests.
class FakeLLMClient:

    def generate_structured(self, prompt, response_schema):
        return response_schema(
            summary="A creative story about friendship and discovery.",
            description=(
                "Two friends explore a mysterious world "
                "and discover unexpected adventures."
            ),
            keywords=[
                "friendship",
                "discovery",
                "adventure",
                "mystery",
                "imagination",
            ],
            themes=[
                "Friendship",
                "Adventure",
                "Discovery",
            ],
            mood_tags=[
                "Curious",
                "Hopeful",
                "Mysterious",
            ],
        )

    def generate_image_structured(
        self,
        prompt,
        image_path,
        response_schema,
    ):
        return response_schema(
            summary="A peaceful blue landscape.",
            description=("A blue landscape with a calm and minimal appearance."),
            keywords=[
                "blue",
                "landscape",
                "minimal",
                "peaceful",
                "nature",
            ],
            themes=[
                "Nature",
                "Minimalism",
            ],
            mood_tags=[
                "Calm",
                "Peaceful",
            ],
        )

    def generate_embedding(self, text):
        return [0.01] * 768


# Fake database: stores records in memory.
class FakeMetadataStore:

    def __init__(self):
        self.records = []

    def save(self, record):
        self.records.append(record)


# Fake URL extractor: avoids external network requests.
class FakeURLExtractor:

    def extract_content(self, url):
        return {
            "title": "Creative Storytelling",
            "url": url,
            "text": (
                "Every great story begins with an idea. "
                "Ideas grow through imagination and creativity."
            ),
            "character_count": 107,
            "word_count": 15,
        }


def create_sample_files(directory):

    # Text file.
    text_path = directory / "story.txt"
    text_path.write_text(
        "Two friends discover a mysterious world.",
        encoding="utf-8",
    )

    # Markdown file.
    markdown_path = directory / "story.md"
    markdown_path.write_text(
        "# A New Beginning\nTwo friends explore a new world.",
        encoding="utf-8",
    )

    # PDF file.
    pdf_path = directory / "story.pdf"

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Two friends discover a mysterious world.",
    )
    document.save(pdf_path)
    document.close()

    # Image file.
    image_path = directory / "landscape.png"

    image = Image.new(
        "RGB",
        (800, 600),
        color="blue",
    )
    image.save(image_path)

    return {
        "text": text_path,
        "markdown": markdown_path,
        "pdf": pdf_path,
        "image": image_path,
    }


def main():

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        files = create_sample_files(temp_path)

        fake_client = FakeLLMClient()
        fake_store = FakeMetadataStore()

        pipeline = InspirationIngestionPipeline(
            llm_client=fake_client,
            metadata_store=fake_store,
        )

        # Keep uploaded originals inside the temporary directory.
        pipeline.file_handler.originals_dir = temp_path / "originals"

        # Replace URL extraction to avoid network access.
        pipeline.url_extractor = FakeURLExtractor()

        # Test text ingestion.
        text_record = pipeline.ingest_file(files["text"])

        assert text_record.content_type == "text"
        assert text_record.embedding is not None
        assert len(text_record.embedding) == 768

        print("TXT ingestion passed:", text_record.file_name)

        # Test Markdown ingestion.
        markdown_record = pipeline.ingest_file(files["markdown"])

        assert markdown_record.content_type == "text"
        assert markdown_record.extracted_text

        print("Markdown ingestion passed:", markdown_record.file_name)

        # Test PDF ingestion.
        pdf_record = pipeline.ingest_file(files["pdf"])

        assert pdf_record.content_type == "pdf"
        assert pdf_record.extracted_text
        assert pdf_record.provenance["extraction_metadata"]["page_count"] == 1

        print("PDF ingestion passed:", pdf_record.file_name)

        # Test image ingestion.
        image_record = pipeline.ingest_file(files["image"])

        assert image_record.content_type == "image"
        assert image_record.summary
        assert image_record.embedding is not None
        assert len(image_record.embedding) == 768

        print("Image ingestion passed:", image_record.file_name)

        # Test URL ingestion.
        url_record = pipeline.ingest_url("https://example.com/story")

        assert url_record.content_type == "url"
        assert url_record.source == "https://example.com/story"
        assert url_record.extracted_text

        print("URL ingestion passed:", url_record.file_name)

        # Verify all records were saved.
        assert len(fake_store.records) == 5

        print("\nTotal records saved:", len(fake_store.records))

        # Verify every record has an embedding.
        for record in fake_store.records:
            assert record.embedding is not None
            assert len(record.embedding) == 768

        print("All records contain 768-dimensional embeddings.")

        # Verify stored original files exist.
        for record in fake_store.records:
            if record.storage_path:
                assert Path(record.storage_path).exists()

        print("Original files successfully preserved.")

    print("\nAll Ingestion Pipeline checks passed!")


if __name__ == "__main__":
    main()
