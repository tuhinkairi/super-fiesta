from modules.inspiration_ingestion.config import get_inspiration_settings


def main():
    settings = get_inspiration_settings()

    print("Configuration loaded successfully!")
    print("Storage directory:", settings.storage_dir)
    print("Maximum file size:", settings.max_file_size_mb, "MB")
    print("Chunk size:", settings.chunk_size)
    print("Chunk overlap:", settings.chunk_overlap)

    assert settings.max_file_size_mb > 0
    assert settings.chunk_size > 0
    assert settings.chunk_overlap < settings.chunk_size

    print("\nAll configuration checks passed!")


if __name__ == "__main__":
    main()
