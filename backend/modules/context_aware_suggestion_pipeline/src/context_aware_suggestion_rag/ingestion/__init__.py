"""
Document ingestion package.

Provides document validation, extraction, chunking,
processing, batch ingestion, and local storage.

Supported document formats:
    - PDF
    - DOCX
    - TXT
    - JSON
"""

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.validators import (
    validate_document_file,
    validate_document_id,
    validate_document_name,
    validate_document_text,
    validate_file_extension,
    validate_file_path,
    validate_file_size,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.models import (
    DocumentSource,
    ExtractionResult,
    IngestionBatch,
    IngestionResult,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.loaders import (
    DocumentLoader,
    load_document,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.chunkers import (
    ChunkingConfig,
    DocumentChunker,
    chunk_document,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.processors import (
    DocumentProcessor,
    process_document,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.batch import (
    BatchDocumentProcessor,
    process_documents,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.storage import (
    IngestionStorage,
    IngestionStorageError,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.ingestion.service import (
    DocumentIngestionService,
)


__all__ = [
    # Validators
    "validate_document_file",
    "validate_document_id",
    "validate_document_name",
    "validate_document_text",
    "validate_file_extension",
    "validate_file_path",
    "validate_file_size",

    # Models
    "DocumentSource",
    "ExtractionResult",
    "IngestionBatch",
    "IngestionResult",

    # Loaders
    "DocumentLoader",
    "load_document",

    # Chunkers
    "ChunkingConfig",
    "DocumentChunker",
    "chunk_document",

    # Processors
    "DocumentProcessor",
    "process_document",

    # Batch processing
    "BatchDocumentProcessor",
    "process_documents",

    # Storage
    "IngestionStorage",
    "IngestionStorageError",

    # Service
    "DocumentIngestionService",
]
