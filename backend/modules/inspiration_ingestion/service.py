from pathlib import Path

from modules.inspiration_ingestion.pipeline.ingestion_pipeline import (
    InspirationIngestionPipeline,
)

from modules.inspiration_ingestion.processing.search_engine import (
    SemanticSearchEngine,
)


class InspirationService:
    """
    Public interface for the Inspiration Ingestion module.

    Provides simple methods for adding, searching,
    retrieving, and listing inspiration records.
    """

    def __init__(self, llm_client=None, metadata_store=None):

        self.pipeline = InspirationIngestionPipeline(
            llm_client=llm_client,
            metadata_store=metadata_store,
        )

        self.search_engine = SemanticSearchEngine(
            metadata_store=self.pipeline.metadata_store,
            embedding_generator=self.pipeline.embedding_generator,
        )

        self.metadata_store = self.pipeline.metadata_store

    def add_file(self, file_path: str | Path):
        """Add a PDF, image, TXT, or Markdown file."""
        return self.pipeline.ingest_file(file_path)

    def add_url(self, url: str):
        """Add inspiration from a webpage."""
        return self.pipeline.ingest_url(url)

    def search(self, query: str, top_k: int = 5):
        """Find inspiration relevant to a natural-language query."""
        return self.search_engine.search(query, top_k)

    def get(self, record_id: str):
        """Retrieve one inspiration record by its ID."""
        return self.metadata_store.get(record_id)

    def list_all(self):
        """Retrieve all saved inspiration records."""
        return self.metadata_store.get_all()

    def close(self):
        """Close the resources owned by this service."""
        self.pipeline.close()
