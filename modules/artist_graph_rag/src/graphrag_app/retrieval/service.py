
from graphrag_app.retrieval.models import (
    RetrievalRequest,
    RetrievalResult,
    RetrievedEntity,
)
from graphrag_app.retrieval.graph_retriever import GraphRetriever


class RetrievalService:
    """Coordinates graph retrieval and context construction."""

    NO_RESULTS_MESSAGE = (
        "No relevant knowledge was found in the knowledge graph."
    )

    def __init__(
        self,
        graph_retriever: GraphRetriever,
    ):
        self.graph_retriever = graph_retriever

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        """Retrieve graph knowledge and build context."""

        entities, relationships = self.graph_retriever.retrieve(
            request
        )

        context = self._build_context(
            entities,
            relationships,
        )

        return RetrievalResult(
            query=request.query,
            entities=entities,
            relationships=relationships,
            context=context,
            total_entities=len(entities),
            total_relationships=len(relationships),
        )

    @classmethod
    def _build_context(
        cls,
        entities: list[RetrievedEntity],
        relationships: list[dict],
    ) -> str:
        """Convert graph results into readable text context."""

        context_parts: list[str] = []

        if entities:
            context_parts.append("ENTITIES:")

            for entity in entities:
                description = (
                    entity.description
                    or "No description available."
                )

                context_parts.append(
                    f"- {entity.name} "
                    f"({entity.entity_type}): {description}"
                )

                if entity.properties:
                    properties = ", ".join(
                        f"{key}={value}"
                        for key, value in sorted(
                            entity.properties.items()
                        )
                    )

                    context_parts.append(
                        f"  Properties: {properties}"
                    )

                if entity.source_document_id:
                    context_parts.append(
                        f"  Source document: "
                        f"{entity.source_document_id}"
                    )

                if entity.source_chunk_id:
                    context_parts.append(
                        f"  Source chunk: {entity.source_chunk_id}"
                    )

        if relationships:
            context_parts.append("\nRELATIONSHIPS:")

            for relationship in relationships:
                source = relationship.get("source", "Unknown")
                relation = relationship.get(
                    "relationship",
                    "RELATED_TO",
                )
                target = relationship.get("target", "Unknown")

                context_parts.append(
                    f"- {source} --[{relation}]--> {target}"
                )

                description = relationship.get("description")

                if description:
                    context_parts.append(
                        f"  Description: {description}"
                    )

        if not context_parts:
            return cls.NO_RESULTS_MESSAGE

        return "\n".join(context_parts)
