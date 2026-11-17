from pathlib import Path
from tempfile import TemporaryDirectory

from modules.inspiration_ingestion.config import InspirationSettings
from modules.inspiration_ingestion.ingestion.file_handler import FileHandler


def main():
    with TemporaryDirectory() as temp_dir:
        test_root = Path(temp_dir)

        # Create a temporary text file to simulate an upload.
        sample_file = test_root / "sample_note.txt"
        sample_file.write_text(
            "A story about friendship and adventure.",
            encoding="utf-8",
        )

        # Use temporary storage so the test doesn't leave files
        # in your actual project storage.
        settings = InspirationSettings(storage_dir=test_root / "storage")

        handler = FileHandler()
        handler.settings = settings
        handler.originals_dir = settings.storage_dir / "originals"

        result = handler.save_file(sample_file)

        print("File saved successfully!")
        print("Original name:", result["file_name"])
        print("Stored name:", result["stored_name"])
        print("Content type:", result["content_type"])
        print("Storage path:", result["storage_path"])
        print("File size:", result["file_size_bytes"], "bytes")

        saved_path = Path(result["storage_path"])

        assert saved_path.exists()
        assert result["content_type"] == "text"
        assert saved_path.read_text(encoding="utf-8") == (
            "A story about friendship and adventure."
        )

        # Verify unsupported file types are rejected.
        unsupported_file = test_root / "sample.exe"
        unsupported_file.write_text("test", encoding="utf-8")

        try:
            handler.save_file(unsupported_file)
            raise AssertionError("Unsupported file was accepted!")
        except ValueError as error:
            print("\nUnsupported file correctly rejected:", error)

        print("\nAll File Handler checks passed!")


if __name__ == "__main__":
    main()
