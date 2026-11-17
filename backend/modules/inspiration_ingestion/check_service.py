from pathlib import Path
from tempfile import TemporaryDirectory

from modules.inspiration_ingestion.service import InspirationService


# Fake AI client: no real Gemini API calls.
class FakeLLMClient:

    def generate_structured(self, prompt, response_schema):
        return response_schema(
            summary="A story about friendship and adventure.",
            description="Two friends explore a mysterious world.",
            keywords=["friendship", "adventure", "mystery"],
            themes=["Friendship", "Discovery"],
            mood_tags=["Curious", "Hopeful"],
        )

    def generate_image_structured(self, prompt, image_path, response_schema):
        return response_schema(
            summary="A peaceful landscape.",
            description="A calm blue landscape.",
            keywords=["blue", "landscape"],
            themes=["Nature"],
            mood_tags=["Peaceful"],
        )

    def generate_embedding(self, text):
        # Consistent fake embedding for testing.
        return [0.01] * 768


# Fake metadata store.
class FakeMetadataStore:

    def __init__(self):
        self.records = {}

    def save(self, record):
        self.records[record.id] = record

    def get(self, record_id):
        return self.records.get(record_id)

    def get_all(self):
        return list(self.records.values())


def main():

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        # Create a sample text file.
        sample_file = temp_path / "idea.txt"
        sample_file.write_text(
            "Two friends discover a mysterious world.",
            encoding="utf-8",
        )

        fake_client = FakeLLMClient()
        fake_store = FakeMetadataStore()

        # Create the public service.
        service = InspirationService(
            llm_client=fake_client,
            metadata_store=fake_store,
        )

        # Keep uploaded files inside the temporary directory.
        service.pipeline.file_handler.originals_dir = temp_path / "originals"

        # Test adding a file.
        record = service.add_file(sample_file)

        assert record.content_type == "text"
        print("Add file passed:", record.file_name)

        # Test retrieving one record.
        retrieved = service.get(record.id)

        assert retrieved is not None
        assert retrieved.id == record.id
        print("Get record passed.")

        # Test listing all records.
        records = service.list_all()

        assert len(records) == 1
        print("List records passed:", len(records))

        # Test semantic search.
        results = service.search(
            "A mysterious adventure about friendship",
            top_k=3,
        )

        assert len(results) == 1
        assert results[0]["record"].id == record.id
        print("Search passed.")

        # Test invalid record ID.
        missing = service.get("invalid-record-id")

        assert missing is None
        print("Missing record check passed.")

        # Close resources.
        service.close()

    print("\nAll InspirationService checks passed!")


if __name__ == "__main__":
    main()
