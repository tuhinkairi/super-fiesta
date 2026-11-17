"""
Domain package.

Provides domain entities, schemas, value objects, factories,
mappers, enumerations, and business rules.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import (
    ContentFormat,
    DocumentType,
    ProcessingStatus,
    RecommendationPriority,
    SourceType,
    WorkflowStatus,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import (
    DomainEntity,
    DocumentEntity,
    DocumentChunkEntity,
    TrendEntity,
    NewsEntity,
    RecommendationEntity,
    GeneratedContentEntity,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.schemas import (
    DomainSchema,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    SuggestionRequest,
    RecommendationResponse,
    GeneratedContentResponse,
    PipelineResponse,
    NewsSourceSchema,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.value_objects import (
    ValueObject,
    LanguageCode,
    RegionCode,
    RelevanceScore,
    TrendTimeRange,
    DocumentMetadata,
    SourceReference,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.factories import (
    create_document,
    create_document_chunk,
    create_trend,
    create_news,
    create_recommendation,
    create_generated_content,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.mappers import (
    DomainMappingError,
    entity_to_dict,
    dict_to_entity,
    document_to_dict,
    document_chunk_to_dict,
    trend_to_dict,
    news_to_dict,
    recommendation_to_dict,
    generated_content_to_dict,
    document_from_dict,
    trend_from_dict,
    news_from_dict,
    recommendation_from_dict,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.rules import (
    DomainRuleViolation,
    validate_document_for_processing,
    validate_trend,
    validate_recommendation,
    validate_generated_content,
    validate_recommendation_content_link,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import current_utc_time


__all__ = [
    # Enumerations
    "ContentFormat",
    "DocumentType",
    "ProcessingStatus",
    "RecommendationPriority",
    "SourceType",
    "WorkflowStatus",

    # Entities
    "DomainEntity",
    "DocumentEntity",
    "DocumentChunkEntity",
    "TrendEntity",
    "NewsEntity",
    "RecommendationEntity",
    "GeneratedContentEntity",
    "current_utc_time",

    # Schemas
    "DomainSchema",
    "DocumentIngestionRequest",
    "DocumentIngestionResponse",
    "SuggestionRequest",
    "RecommendationResponse",
    "GeneratedContentResponse",
    "PipelineResponse",
    "NewsSourceSchema",

    # Value objects
    "ValueObject",
    "LanguageCode",
    "RegionCode",
    "RelevanceScore",
    "TrendTimeRange",
    "DocumentMetadata",
    "SourceReference",

    # Factories
    "create_document",
    "create_document_chunk",
    "create_trend",
    "create_news",
    "create_recommendation",
    "create_generated_content",

    # Mappers
    "DomainMappingError",
    "entity_to_dict",
    "dict_to_entity",
    "document_to_dict",
    "document_chunk_to_dict",
    "trend_to_dict",
    "news_to_dict",
    "recommendation_to_dict",
    "generated_content_to_dict",
    "document_from_dict",
    "trend_from_dict",
    "news_from_dict",
    "recommendation_from_dict",

    # Business rules
    "DomainRuleViolation",
    "validate_document_for_processing",
    "validate_trend",
    "validate_recommendation",
    "validate_generated_content",
    "validate_recommendation_content_link",
]
