from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)


class GraphRetriever:
    """
    Retrieves information from an in-memory story knowledge graph.
    """

    def __init__(self, graph: StoryKnowledgeGraph):

        self.graph = graph

        # Create an index for fast node lookup.
        self.nodes_by_id = {node.id: node for node in graph.nodes}

        # Validate node IDs.
        if len(self.nodes_by_id) != len(graph.nodes):
            raise ValueError("Duplicate node IDs found.")

        # Validate edge IDs and references.
        edge_ids = [edge.id for edge in graph.edges]

        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Duplicate edge IDs found.")

        for edge in graph.edges:

            if edge.source_id not in self.nodes_by_id:
                raise ValueError(f"Unknown source node: {edge.source_id}")

            if edge.target_id not in self.nodes_by_id:
                raise ValueError(f"Unknown target node: {edge.target_id}")

    def find_nodes(
        self,
        label: str,
        node_type: str | None = None,
    ) -> list[GraphNode]:
        """Find nodes by their label and optional type."""

        normalized_label = label.strip().casefold()

        return [
            node
            for node in self.graph.nodes
            if (
                node.label.strip().casefold() == normalized_label
                and (node_type is None or node.node_type == node_type)
            )
        ]

    def get_character(
        self,
        name: str,
    ) -> GraphNode | None:
        """Find a character by primary name or known alias."""

        candidates = [
            node for node in self.graph.nodes if node.node_type == "character"
        ]

        normalized_name = name.strip().casefold()

        for node in candidates:

            if node.label.strip().casefold() == normalized_name:
                return node

            aliases = node.properties.get("aliases", [])

            if any(alias.strip().casefold() == normalized_name for alias in aliases):
                return node

        return None

    def get_relationships(
        self,
        character_name: str,
    ) -> list[GraphEdge]:
        """Retrieve relationships connected to a character."""

        character = self.get_character(character_name)

        if character is None:
            return []

        return [
            edge
            for edge in self.graph.edges
            if edge.edge_type
            not in {
                "PARTICIPATED_IN",
                "OCCURRED_AT",
            }
            and (edge.source_id == character.id or edge.target_id == character.id)
        ]

    def get_related_characters(
        self,
        character_name: str,
    ) -> list[GraphNode]:
        """Find characters connected through relationships."""

        relationships = self.get_relationships(character_name)

        related_nodes = []
        seen = set()

        character = self.get_character(character_name)

        if character is None:
            return []

        for edge in relationships:

            other_id = (
                edge.target_id if edge.source_id == character.id else edge.source_id
            )

            node = self.nodes_by_id.get(other_id)

            if node and node.node_type == "character" and node.id not in seen:
                seen.add(node.id)
                related_nodes.append(node)

        return related_nodes

    def get_events_for_character(
        self,
        character_name: str,
    ) -> list[GraphNode]:
        """Retrieve all events involving a character."""

        character = self.get_character(character_name)

        if character is None:
            return []

        events = []

        for edge in self.graph.edges:

            if edge.edge_type == "PARTICIPATED_IN" and edge.source_id == character.id:
                event = self.nodes_by_id.get(edge.target_id)

                if event and event.node_type == "event":
                    events.append(event)

        return events

    def get_events_in_chapter(
        self,
        chapter_number: int,
    ) -> list[GraphNode]:
        """Retrieve events from a particular chapter."""

        return [
            node
            for node in self.graph.nodes
            if (
                node.node_type == "event"
                and node.properties.get("chapter_number") == chapter_number
            )
        ]

    def get_location_for_event(
        self,
        event_id: str,
    ) -> GraphNode | None:
        """Find the location associated with an event."""

        event = self.nodes_by_id.get(event_id)

        if event is None or event.node_type != "event":
            return None

        for edge in self.graph.edges:

            if edge.source_id == event_id and edge.edge_type == "OCCURRED_AT":
                return self.nodes_by_id.get(edge.target_id)

        return None
