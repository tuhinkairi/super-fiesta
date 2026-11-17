from pathlib import Path
from urllib.parse import urlparse

from modules.story_intelligence.llm.llm_client import LLMClient

from modules.inspiration_ingestion.types import InspirationRecord

from modules.inspiration_ingestion.ingestion.file_handler import (
    FileHandler,
)

from modules.inspiration_ingestion.extractors.pdf_extractor import (
    PDFExtractor,
)

from modules.inspiration_ingestion.extractors.text_extractor import (
    TextExtractor,
)

from modules.inspiration_ingestion.extractors.url_extractor import (
    URLExtractor,
)

from modules.inspiration_ingestion.processing.analyzer import (
    InspirationAnalyzer,
)

from modules.inspiration_ingestion.processing.image_analyzer import (
    ImageAnalyzer,
)

from modules.inspiration_ingestion.processing.embedding_generator import (
    EmbeddingGenerator,
)

from modules.inspiration_ingestion.repositories.metadata_store import (
    MetadataStore,
)


class InspirationIngestionPipeline:
    """
    Coordinates the complete inspiration ingestion process.
    """

    def __init__(self, llm_client=None, metadata_store=None):

        # Use one shared Gemini client across all AI components.
        self._owns_llm_client = llm_client is None
        self.llm_client = llm_client or LLMClient()

        self.file_handler = FileHandler()
        self.pdf_extractor = PDFExtractor()
        self.text_extractor = TextExtractor()
        self.url_extractor = URLExtractor()

        self.text_analyzer = InspirationAnalyzer(llm_client=self.llm_client)

        self.image_analyzer = ImageAnalyzer(llm_client=self.llm_client)

        self.embedding_generator = EmbeddingGenerator(llm_client=self.llm_client)

        self.metadata_store = metadata_store or MetadataStore()

    @staticmethod
    def _build_embedding_text(analysis) -> str:
        """
        Combine meaningful AI metadata for embedding generation.
        """

        return "\n".join(
            [
                analysis.summary,
                analysis.description,
                "Keywords: " + ", ".join(analysis.keywords),
                "Themes: " + ", ".join(analysis.themes),
                "Mood: " + ", ".join(analysis.mood_tags),
            ]
        )

    def _save_record(
        self,
        file_name: str,
        content_type: str,
        extracted_text: str,
        analysis,
        embedding: list[float],
        source: str | None = None,
        storage_path: str | None = None,
        provenance: dict | None = None,
    ) -> InspirationRecord:

        record = InspirationRecord(
            file_name=file_name,
            content_type=content_type,
            source=source,
            storage_path=storage_path,
            extracted_text=extracted_text,
            summary=analysis.summary,
            description=analysis.description,
            keywords=analysis.keywords,
            themes=analysis.themes,
            mood_tags=analysis.mood_tags,
            provenance=provenance or {},
            embedding=embedding,
        )

        self.metadata_store.save(record)

        return record

    def ingest_file(
        self,
        source_path: str | Path,
    ) -> InspirationRecord:
        """
        Ingest a PDF, image, TXT, or Markdown file.
        """

        # Step 1: Validate and store the original file.
        saved_file = self.file_handler.save_file(source_path)

        content_type = saved_file["content_type"]
        storage_path = saved_file["storage_path"]

        # Step 2: Extract content and generate AI analysis.
        if content_type == "pdf":

            extraction = self.pdf_extractor.extract_text(storage_path)

            if not extraction["has_text"]:
                raise ValueError(
                    "No readable text found in PDF. " "Scanned PDFs require OCR."
                )

            extracted_text = extraction["text"]

            analysis = self.text_analyzer.analyze_text(extracted_text)

            extraction_metadata = {
                "page_count": extraction["page_count"],
            }

        elif content_type == "text":

            extraction = self.text_extractor.extract_text(storage_path)

            extracted_text = extraction["text"]

            if not extracted_text:
                raise ValueError("The uploaded text file is empty.")

            analysis = self.text_analyzer.analyze_text(extracted_text)

            extraction_metadata = {
                "character_count": extraction["character_count"],
                "word_count": extraction["word_count"],
            }

        elif content_type == "image":

            analysis = self.image_analyzer.analyze_image(storage_path)

            # Use the image description as searchable text.
            extracted_text = analysis.description

            extraction_metadata = {
                "image_analysis": "Gemini multimodal analysis",
            }

        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Step 3: Generate semantic embedding.
        embedding_text = self._build_embedding_text(analysis)

        embedding = self.embedding_generator.generate(embedding_text)

        # Step 4: Save complete metadata.
        return self._save_record(
            file_name=saved_file["file_name"],
            content_type=content_type,
            extracted_text=extracted_text,
            analysis=analysis,
            embedding=embedding,
            source="Local upload",
            storage_path=storage_path,
            provenance={
                "original_file": saved_file["file_name"],
                "stored_name": saved_file["stored_name"],
                "file_size_bytes": saved_file["file_size_bytes"],
                "extraction_metadata": extraction_metadata,
            },
        )

    def ingest_url(self, url: str) -> InspirationRecord:
        """
        Ingest a webpage using its URL.
        """

        # Step 1: Extract webpage content.
        extraction = self.url_extractor.extract_content(url)

        extracted_text = extraction["text"]

        # Step 2: Analyze webpage content.
        analysis = self.text_analyzer.analyze_text(extracted_text)

        # Step 3: Generate embedding.
        embedding_text = self._build_embedding_text(analysis)

        embedding = self.embedding_generator.generate(embedding_text)

        parsed_url = urlparse(extraction["url"])

        file_name = (
            extraction["title"] or Path(parsed_url.path).name or parsed_url.netloc
        )

        # Step 4: Save webpage metadata.
        return self._save_record(
            file_name=file_name,
            content_type="url",
            extracted_text=extracted_text,
            analysis=analysis,
            embedding=embedding,
            source=extraction["url"],
            provenance={
                "source_url": extraction["url"],
                "page_title": extraction["title"],
                "character_count": extraction["character_count"],
                "word_count": extraction["word_count"],
            },
        )

    def close(self):
        """
        Close the shared Gemini client if owned by this pipeline.
        """

        if self._owns_llm_client:
            self.llm_client.close()
