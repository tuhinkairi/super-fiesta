"""Database package public exports."""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import (
    current_utc_time,
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
    VectorSearchResult,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.base import (
    BaseVectorDatabase,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.connection import (
    PineconeConnection,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.index_manager import (
    PineconeIndexManager,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.pinecone_store import (
    PineconeVectorStore,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.repository import (
    VectorRepository,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.utils import (
    validate_dense_vector,
    validate_sparse_vector,
    validate_vector_record,
    group_records_by_namespace,
    prepare_metadata,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.filters import (
    validate_metadata_filter,
    build_metadata_filter,
    combine_filters,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.namespaces import (
    NamespaceManager,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.batch import (
    BatchResult,
    VectorBatchProcessor,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.health import (
    DatabaseHealth,
    DatabaseHealthChecker,
)

__all__ = [
    "current_utc_time",
    "DatabaseOperationResult",
    "VectorQueryResult",
    "VectorRecord",
    "VectorSearchResult",
    "BaseVectorDatabase",
    "PineconeConnection",
    "PineconeIndexManager",
    "PineconeVectorStore",
    "VectorRepository",
    "validate_dense_vector",
    "validate_sparse_vector",
    "validate_vector_record",
    "group_records_by_namespace",
    "prepare_metadata",
    "validate_metadata_filter",
    "build_metadata_filter",
    "combine_filters",
    "NamespaceManager",
    "BatchResult",
    "VectorBatchProcessor",
    "DatabaseHealth",
    "DatabaseHealthChecker",
]
