from pathlib import Path
from tempfile import TemporaryDirectory

from modules.inspiration_ingestion.service import InspirationService
from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)

SAMPLE_TEXT = """
Artificial intelligence is transforming the way people learn,
work, and interact with technology.

In education, AI-powered learning systems can provide personalized
recommendations based on individual student performance. These
systems help students identify their weaknesses and learn at
their own pace.

In healthcare, artificial intelligence can assist doctors
in analyzing medical images, identifying patterns, and supporting
clinical decisions.

However, the development of AI also raises important concerns.
Data privacy, algorithmic bias, transparency, and accountability
must be considered when designing intelligent systems.

Responsible AI development requires a balance between technological
innovation, human values, fairness, and social responsibility.

The future of artificial intelligence should focus not only on
automation but also on improving human capabilities and creating
positive social impact.
"""


def main():
    service = None

    try:
        with TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            # 1. Create an isolated TXT file.
            source_file = temp_path / "ai_responsibility.txt"
            source_file.write_text(
                SAMPLE_TEXT,
                encoding="utf-8",
            )

            # 2. Create an isolated SQLite database.
            database_path = temp_path / "test_inspiration.db"
            metadata_store = MetadataStore(db_path=database_path)

            # 3. Initialize the actual service.
            service = InspirationService(metadata_store=metadata_store)

            # Redirect uploaded files to temporary storage.
            service.pipeline.file_handler.originals_dir = temp_path / "originals"

            print("\n[1/4] Ingesting TXT file...")
            record = service.add_file(source_file)

            print("File ingestion completed.")
            print("Record ID:", record.id)
            print("File name:", record.file_name)
            print("Content type:", record.content_type)

            assert record.content_type == "text"
            assert record.extracted_text
            print("PASS: Text extraction completed.")

            # 4. Verify Gemini analysis.
            print("\n[2/4] Checking Gemini analysis...")

            print("\nSummary:")
            print(record.summary)

            print("\nKeywords:")
            print(record.keywords)

            print("\nThemes:")
            print(record.themes)

            assert record.summary.strip()
            assert record.description.strip()
            assert record.keywords
            assert record.themes
            assert record.embedding
            assert len(record.embedding) == 768

            print("PASS: Structured analysis generated.")
            print("PASS: 768-dimensional embedding generated.")

            # 5. Verify SQLite persistence.
            print("\n[3/4] Checking SQLite persistence...")

            saved_record = metadata_store.get(record.id)

            assert saved_record is not None
            assert saved_record.id == record.id
            assert saved_record.summary == record.summary
            assert saved_record.embedding == record.embedding

            assert metadata_store.count() == 1

            print("PASS: Record retrieved from SQLite.")
            print("PASS: Embedding and metadata persisted.")

            # 6. Verify semantic search.
            print("\n[4/4] Testing semantic search...")

            results = service.search(
                "How can artificial intelligence improve education "
                "while maintaining fairness and responsibility?",
                top_k=1,
            )

            assert results, "Semantic search returned no results."

            best_result = results[0]
            matched_record = best_result["record"]
            similarity = best_result["similarity"]

            print("\nBest search result:")
            print("File:", matched_record.file_name)
            print("Similarity:", similarity)
            print("Summary:", matched_record.summary)

            assert matched_record.id == record.id

            print("\nPASS: Semantic search returned the expected record.")

            print("\n========================================")
            print("LIVE TEXT INGESTION TEST PASSED")
            print("========================================")
            print("Expected Gemini operations: 3")
            print("Text analysis: 1")
            print("Document embedding: 1")
            print("Search-query embedding: 1")
            print("SQLite operations: Local only")

    finally:
        if service is not None:
            service.close()


if __name__ == "__main__":
    main()
