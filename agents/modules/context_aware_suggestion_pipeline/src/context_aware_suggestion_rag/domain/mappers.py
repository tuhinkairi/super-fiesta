"""
Domain mappers.

Converts domain entities to dictionaries and reconstructs
validated entities from dictionaries.
"""

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.entities import (
    DocumentChunkEntity,
    DocumentEntity,
    GeneratedContentEntity,
    NewsEntity,
    RecommendationEntity,
    TrendEntity,
)

EntityT = TypeVar("EntityT", bound=BaseModel)


class DomainMappingError(ValueError):
    """Raised when domain entity mapping fails."""


def entity_to_dict(entity: BaseModel) -> dict[str, Any]:
    """Convert a Pydantic domain entity into a Python dictionary."""
    if not isinstance(entity, BaseModel):
        raise DomainMappingError(
            "Expected a Pydantic model instance."
        )

    try:
        return entity.model_dump(mode="json")
    except (TypeError, ValueError) as exc:
        raise DomainMappingError(
            f"Unable to serialize {type(entity).__name__}."
        ) from exc


def dict_to_entity(
    data: dict[str, Any],
    entity_class: type[EntityT],
) -> EntityT:
    """Validate a dictionary and convert it into a domain entity."""
    if not isinstance(data, dict):
        raise DomainMappingError("Input data must be a dictionary.")

    if not isinstance(entity_class, type) or not issubclass(
        entity_class, BaseModel
    ):
        raise DomainMappingError(
            "Entity class must be a Pydantic model."
        )

    try:
        return entity_class.model_validate(data)
    except ValidationError as exc:
        raise DomainMappingError(
            f"Unable to construct {entity_class.__name__}."
        ) from exc


def document_to_dict(entity: DocumentEntity) -> dict[str, Any]:
    return entity_to_dict(entity)


def document_chunk_to_dict(
    entity: DocumentChunkEntity,
) -> dict[str, Any]:
    return entity_to_dict(entity)


def trend_to_dict(entity: TrendEntity) -> dict[str, Any]:
    return entity_to_dict(entity)


def news_to_dict(entity: NewsEntity) -> dict[str, Any]:
    return entity_to_dict(entity)


def recommendation_to_dict(
    entity: RecommendationEntity,
) -> dict[str, Any]:
    return entity_to_dict(entity)


def generated_content_to_dict(
    entity: GeneratedContentEntity,
) -> dict[str, Any]:
    return entity_to_dict(entity)


def document_from_dict(data: dict[str, Any]) -> DocumentEntity:
    return dict_to_entity(data, DocumentEntity)


def trend_from_dict(data: dict[str, Any]) -> TrendEntity:
    return dict_to_entity(data, TrendEntity)


def news_from_dict(data: dict[str, Any]) -> NewsEntity:
    return dict_to_entity(data, NewsEntity)


def recommendation_from_dict(
    data: dict[str, Any],
) -> RecommendationEntity:
    return dict_to_entity(data, RecommendationEntity)


__all__ = [
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
]
