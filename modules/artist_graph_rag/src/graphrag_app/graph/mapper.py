
import hashlib
import re

from graphrag_app.extraction.models import ChunkExtractionResult
from graphrag_app.graph.schema import Entity, Relationship


class GraphMapper:
    """Converts extraction results into knowledge graph models."""

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize an entity name for consistent identification."""

        return re.sub(r"\s+", " ", name.strip()).casefold()

    @staticmethod
    def _generate_id(value: str) -> str:
        """Generate a deterministic ID from a string."""

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    def map_extraction(
        self,
        result: ChunkExtractionResult,
    ) -> tuple[list[Entity], list[Relationship]]:
        """Convert extraction results into graph models."""

        entities_by_identity: dict[tuple[str, str], Entity] = {}
        entities_by_name: dict[str, list[Entity]] = {}

        graph_entities: list[Entity] = []

        # Step 1: Convert and deduplicate entities.
        for extracted in result.entities:
            normalized_name = self._normalize_name(
                extracted.name
            )
            normalized_type = self._normalize_name(
                extracted.entity_type
            )

            if not normalized_name or not normalized_type:
                continue

            identity = (normalized_type, normalized_name)

            # Avoid duplicate entities within the same extraction.
            if identity in entities_by_identity:
                continue

            entity_id = self._generate_id(
                f"{normalized_type}:{normalized_name}"
            )

            entity = Entity(
                id=entity_id,
                name=extracted.name.strip(),
                entity_type=extracted.entity_type.strip(),
                description=extracted.description,
                properties=extracted.properties,
                source_document_id=result.document_id,
                source_chunk_id=result.chunk_id,
            )

            entities_by_identity[identity] = entity

            entities_by_name.setdefault(
                normalized_name, []
            ).append(entity)

            graph_entities.append(entity)

        # Step 2: Convert relationships.
        graph_relationships: list[Relationship] = []
        seen_relationship_ids: set[str] = set()

        for extracted in result.relationships:
            source_name = self._normalize_name(
                extracted.source_entity_name
            )
            target_name = self._normalize_name(
                extracted.target_entity_name
            )

            relation_type = extracted.relation_type.strip().upper()

            if not source_name or not target_name or not relation_type:
                continue

            source_candidates = entities_by_name.get(
                source_name, []
            )
            target_candidates = entities_by_name.get(
                target_name, []
            )

            # Resolve only uniquely identifiable entities.
            if (
                len(source_candidates) != 1
                or len(target_candidates) != 1
            ):
                continue

            source_entity = source_candidates[0]
            target_entity = target_candidates[0]

            identity = (
                f"{result.document_id}:"
                f"{result.chunk_id}:"
                f"{source_entity.id}:"
                f"{relation_type}:"
                f"{target_entity.id}"
            )

            relationship_id = self._generate_id(identity)

            if relationship_id in seen_relationship_ids:
                continue

            relationship = Relationship(
                id=relationship_id,
                source_entity_id=source_entity.id,
                target_entity_id=target_entity.id,
                relation_type=relation_type,
                description=extracted.description,
                properties=extracted.properties,
                source_document_id=result.document_id,
                source_chunk_id=result.chunk_id,
            )

            graph_relationships.append(relationship)
            seen_relationship_ids.add(relationship_id)

        return graph_entities, graph_relationships
