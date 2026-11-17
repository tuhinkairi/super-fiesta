from tempfile import TemporaryDirectory
from pathlib import Path

from modules.inspiration_ingestion.types import InspirationRecord

from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)


def main():

    with TemporaryDirectory() as temp_dir:

        # Use a temporary database so the real project database
        # remains untouched during testing.
        db_path = Path(temp_dir) / "test_inspiration.db"

        store = MetadataStore(db_path=db_path)

        print("Database initialized successfully!")

        # Create a sample inspiration record.
        record = InspirationRecord(
            file_name="story_ideas.pdf",
            content_type="pdf",
            source="Local upload",
            storage_path="storage/originals/pdfs/story_ideas.pdf",
            extracted_text="Two friends discover a mysterious world.",
            summary="A story about two friends and discovery.",
            description="A creative adventure about friendship.",
            keywords=["friendship", "adventure", "mystery"],
            themes=["Friendship", "Discovery"],
            mood_tags=["Curious", "Hopeful"],
            provenance={
                "original_file": "story_ideas.pdf",
                "processing_method": "PDF extraction",
            },
            embedding=[0.12, 0.45, 0.78],
        )

        # Save the record.
        store.save(record)

        print("\nRecord saved successfully!")
        print("Total records:", store.count())

        # Retrieve the record.
        retrieved = store.get(record.id)

        assert retrieved is not None
        assert retrieved.id == record.id
        assert retrieved.file_name == record.file_name
        assert retrieved.keywords == record.keywords
        assert retrieved.themes == record.themes
        assert retrieved.embedding == record.embedding
        assert retrieved.provenance == record.provenance

        print("\nRecord retrieved successfully!")
        print("File name:", retrieved.file_name)
        print("Summary:", retrieved.summary)
        print("Keywords:", retrieved.keywords)
        print("Embedding:", retrieved.embedding)

        # Test updating an existing record.
        retrieved.summary = "Updated summary about discovery."
        store.save(retrieved)

        updated = store.get(record.id)

        assert updated.summary == "Updated summary about discovery."

        print("\nRecord update successful!")
        print("Updated summary:", updated.summary)

        # Test retrieving all records.
        all_records = store.get_all()

        assert len(all_records) == 1
        assert all_records[0].id == record.id

        print("\nAll records retrieved successfully!")
        print("Total records:", len(all_records))

        # Test missing record.
        missing = store.get("non-existent-id")

        assert missing is None

        print("Missing record correctly returned None.")

    print("\nAll Metadata Store checks passed!")


if __name__ == "__main__":
    main()
