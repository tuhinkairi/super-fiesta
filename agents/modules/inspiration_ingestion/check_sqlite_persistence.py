
from tempfile import TemporaryDirectory
from pathlib import Path

from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)

from modules.inspiration_ingestion.types import InspirationRecord


def main():

    with TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "test_inspiration.db"

        # Step 1: Create the database.
        store = MetadataStore(db_path=db_path)

        assert db_path.exists()
        print("Database creation passed.")

        # Step 2: Create a sample inspiration record.
        record = InspirationRecord(
            file_name="friendship_idea.txt",
            content_type="text",
            source="Local upload",
            extracted_text="Two friends discover a hidden world.",
            summary="A story about friendship and discovery.",
            description="Two friends explore a mysterious world.",
            keywords=["friendship", "discovery", "adventure"],
            themes=["Friendship", "Adventure"],
            mood_tags=["Curious", "Hopeful"],
            provenance={"test": True},
            embedding=[0.01] * 768,
        )

        # Step 3: Save the record.
        store.save(record)

        assert store.count() == 1
        print("Record saving passed.")

        # Step 4: Create a NEW store instance.
        # This verifies that data is actually persisted in SQLite.
        new_store = MetadataStore(db_path=db_path)

        retrieved = new_store.get(record.id)

        assert retrieved is not None
        assert retrieved.id == record.id
        assert retrieved.file_name == "friendship_idea.txt"
        assert len(retrieved.embedding) == 768

        print("Persistence across store instances passed.")

        # Step 5: Update the record.
        retrieved.summary = "An updated friendship story."

        new_store.save(retrieved)

        updated = store.get(record.id)

        assert updated.summary == "An updated friendship story."

        print("Record update passed.")

        # Step 6: Test listing.
        all_records = new_store.get_all()

        assert len(all_records) == 1
        print("Record listing passed.")

        # Step 7: Test missing record.
        missing = new_store.get("non-existent-id")

        assert missing is None
        print("Missing record check passed.")

        print("\nTotal records in database:", new_store.count())

    print("\nAll SQLite persistence checks passed!")


if __name__ == "__main__":
    main()
