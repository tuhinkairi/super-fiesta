from typing import Any

from modules.artist_graph_rag.src.graphrag_app.database import Neo4jClient
from modules.artist_graph_rag.src.graphrag_app.retrieval.models import (
    RetrievalRequest,
    RetrievedEntity,
)


class GraphRetriever:
    """Retrieves relevant entities and relationships from Neo4j."""

    def __init__(self, client: Neo4jClient):
        self.client = client

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[list[RetrievedEntity], list[dict]]:
        """Retrieve entities matching a user's query."""

        search_query = request.query.strip()

        if not search_query:
            raise ValueError("Search query cannot be empty.")

        if request.top_k < 1:
            raise ValueError("top_k must be greater than zero.")

        query = """
        MATCH (e:Entity)

        WHERE
            (
                toLower(e.name) CONTAINS toLower($search_query)
                OR
                toLower(coalesce(e.description, ''))
                    CONTAINS toLower($search_query)
            )
            AND
            (
                $document_id IS NULL
                OR e.source_document_id = $document_id
            )

        OPTIONAL MATCH (e)-[r:RELATED_TO]-(connected:Entity)

        RETURN
            e.id AS entity_id,
            e.name AS name,
            e.entity_type AS entity_type,
            e.description AS description,
            properties(e) AS properties,
            e.source_document_id AS source_document_id,
            e.source_chunk_id AS source_chunk_id,

            collect(DISTINCT
                CASE
                    WHEN r IS NOT NULL THEN {
                        source: startNode(r).name,
                        relationship: r.relation_type,
                        target: endNode(r).name
                    }
                END
            ) AS relationships

        ORDER BY e.name
        LIMIT $top_k
        """

        records = self.client.execute_query(
            query,
            {
                "search_query": search_query,
                "document_id": request.document_id,
                "top_k": request.top_k,
            },
        )

        entities: list[RetrievedEntity] = []
        relationships: list[dict] = []
        seen_relationships: set[tuple] = set()

        for record in records:
            entity = RetrievedEntity(
                entity_id=record["entity_id"],
                name=record["name"],
                entity_type=record["entity_type"],
                description=record["description"],
                properties=self._extract_properties(record["properties"] or {}),
                source_document_id=record["source_document_id"],
                source_chunk_id=record["source_chunk_id"],
            )

            entities.append(entity)

            for relationship in record["relationships"]:
                if not relationship:
                    continue

                relationship_type = relationship["relationship"]

                if not relationship_type:
                    continue

                key = (
                    relationship["source"],
                    relationship_type,
                    relationship["target"],
                )

                if key not in seen_relationships:
                    seen_relationships.add(key)
                    relationships.append(relationship)

        return entities, relationships

    @staticmethod
    def _extract_properties(
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Remove internal graph fields from entity properties."""

        internal_fields = {
            "id",
            "name",
            "entity_type",
            "description",
            "source_document_id",
            "source_chunk_id",
        }

        return {
            key: value
            for key, value in properties.items()
            if key not in internal_fields
            and (
                isinstance(value, (str, int, float, bool))
                or (
                    isinstance(value, list)
                    and all(isinstance(item, (str, int, float, bool)) for item in value)
                )
            )
        }
