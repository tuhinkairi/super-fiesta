from typing import Any

from neo4j import ManagedTransaction

from modules.artist_graph_rag.src.graphrag_app.database import Neo4jClient
from modules.artist_graph_rag.src.graphrag_app.graph.schema import Entity, Relationship


class GraphService:
    """Manages knowledge graph creation and storage in Neo4j."""

    ENTITY_QUERY = """
    MERGE (e:Entity {id: $id})
    SET e.name = $name,
        e.entity_type = $entity_type,
        e.description = $description,
        e.source_document_id = $source_document_id,
        e.source_chunk_id = $source_chunk_id
    SET e += $properties
    RETURN e.id AS id, e.name AS name
    """

    RELATIONSHIP_QUERY = """
    MATCH (source:Entity {id: $source_id})
    MATCH (target:Entity {id: $target_id})

    MERGE (source)-[r:RELATED_TO {id: $id}]->(target)

    SET r.relation_type = $relation_type,
        r.description = $description,
        r.source_document_id = $source_document_id,
        r.source_chunk_id = $source_chunk_id

    SET r += $properties

    RETURN source.name AS source,
           r.relation_type AS relationship,
           target.name AS target
    """

    def __init__(self, client: Neo4jClient):
        self.client = client

    @staticmethod
    def _safe_properties(
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Keep only Neo4j-compatible property values."""

        safe: dict[str, Any] = {}

        for key, value in properties.items():
            if not isinstance(key, str) or not key.strip():
                continue

            if isinstance(value, (str, int, float, bool)):
                safe[key] = value

            elif isinstance(value, list) and all(
                isinstance(item, (str, int, float, bool)) for item in value
            ):
                safe[key] = value

        return safe

    @classmethod
    def _entity_parameters(
        cls,
        entity: Entity,
    ) -> dict[str, Any]:
        """Build Neo4j parameters for an entity."""

        return {
            "id": entity.id,
            "name": entity.name,
            "entity_type": entity.entity_type,
            "description": entity.description,
            "source_document_id": entity.source_document_id,
            "source_chunk_id": entity.source_chunk_id,
            "properties": cls._safe_properties(entity.properties),
        }

    @classmethod
    def _relationship_parameters(
        cls,
        relationship: Relationship,
    ) -> dict[str, Any]:
        """Build Neo4j parameters for a relationship."""

        return {
            "id": relationship.id,
            "source_id": relationship.source_entity_id,
            "target_id": relationship.target_entity_id,
            "relation_type": relationship.relation_type,
            "description": relationship.description,
            "source_document_id": relationship.source_document_id,
            "source_chunk_id": relationship.source_chunk_id,
            "properties": cls._safe_properties(relationship.properties),
        }

    def store_entity(self, entity: Entity) -> list[dict]:
        """Create or update an entity node."""

        return self.client.execute_query(
            self.ENTITY_QUERY,
            self._entity_parameters(entity),
        )

    def store_relationship(
        self,
        relationship: Relationship,
    ) -> list[dict]:
        """Create or update a relationship between entities."""

        result = self.client.execute_query(
            self.RELATIONSHIP_QUERY,
            self._relationship_parameters(relationship),
        )

        if not result:
            raise ValueError(
                "Relationship could not be created. "
                "Check whether both entity IDs exist in Neo4j."
            )

        return result

    def store_graph(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> dict[str, int]:
        """Store entities and relationships atomically."""

        def transaction_work(
            tx: ManagedTransaction,
        ) -> dict[str, int]:
            # Store entities first.
            for entity in entities:
                result = tx.run(
                    self.ENTITY_QUERY,
                    self._entity_parameters(entity),
                ).data()

                if not result:
                    raise RuntimeError(f"Failed to store entity: {entity.name}")

            # Store relationships after their endpoint entities.
            for relationship in relationships:
                result = tx.run(
                    self.RELATIONSHIP_QUERY,
                    self._relationship_parameters(relationship),
                ).data()

                if not result:
                    raise ValueError(
                        "Relationship could not be created. "
                        f"Source ID: {relationship.source_entity_id}, "
                        f"Target ID: {relationship.target_entity_id}"
                    )

            return {
                "entities_stored": len(entities),
                "relationships_stored": len(relationships),
            }

        return self.client.execute_transaction(transaction_work)
