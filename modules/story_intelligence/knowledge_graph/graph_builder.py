
from uuid import NAMESPACE_URL, uuid5

from modules.story_intelligence.models.character import (
    CharacterExtractionResult,
)

from modules.story_intelligence.models.relationship import (
    RelationshipExtractionResult,
)

from modules.story_intelligence.models.event import (
    EventExtractionResult,
)

from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)


class GraphBuilder:
    """
    Converts extracted characters, relationships and events
    into a structured story knowledge graph.
    """

    # These relationships are treated as symmetric.
    SYMMETRIC_RELATIONS = {
        "SIBLING_OF",
        "SPOUSE_OF",
        "FRIEND_OF",
        "ALLY_OF",
        "ENEMY_OF",
        "RIVAL_OF",
        "KNOWS",
        "ROMANTIC_INTEREST_OF",
        "WORKS_WITH",
    }

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().split())

    @staticmethod
    def _make_id(
        project_id: str,
        category: str,
        value: str,
    ) -> str:
        """
        Create a deterministic ID for graph entities.
        """

        unique_value = (
            f"{project_id}:{category}:{value.casefold().strip()}"
        )

        return str(uuid5(NAMESPACE_URL, unique_value))

    @classmethod
    def build(
        cls,
        characters: CharacterExtractionResult,
        relationships: RelationshipExtractionResult,
        events: EventExtractionResult,
        project_id: str = "default-project",
    ) -> StoryKnowledgeGraph:

        nodes = []
        edges = []
        warnings = []

        character_ids = {}
        alias_lookup = {}

        # ------------------------------------------------
        # 1. Create character nodes.
        # ------------------------------------------------

        for character in characters.characters:

            normalized_name = cls._normalize(character.name)

            if not normalized_name:
                warnings.append("Empty character name encountered.")
                continue

            character_id = cls._make_id(
                project_id,
                "character",
                normalized_name,
            )

            if normalized_name in character_ids:
                warnings.append(
                    f"Duplicate character record: {character.name}"
                )
                continue

            character_ids[normalized_name] = character_id

            node = GraphNode(
                id=character_id,
                node_type="character",
                label=character.name,
                properties={
                    "aliases": character.aliases,
                    "role_in_story": character.role_in_story,
                    "description": character.description,
                    "personality_traits": character.personality_traits,
                },
            )

            nodes.append(node)

            # Map primary names and aliases to canonical IDs.
            alias_lookup[normalized_name] = character_id

            for alias in character.aliases:
                normalized_alias = cls._normalize(alias)

                if normalized_alias in alias_lookup:
                    warnings.append(
                        f"Ambiguous character alias: {alias}"
                    )
                    continue

                alias_lookup[normalized_alias] = character_id

        # ------------------------------------------------
        # 2. Create character relationship edges.
        # ------------------------------------------------

        seen_relationships = set()

        for relationship in relationships.relationships:

            source_name = cls._normalize(
                relationship.source_character
            )

            target_name = cls._normalize(
                relationship.target_character
            )

            source_id = alias_lookup.get(source_name)
            target_id = alias_lookup.get(target_name)

            if source_id is None or target_id is None:
                warnings.append(
                    "Relationship skipped because a character "
                    "could not be found."
                )
                continue

            if source_id == target_id:
                warnings.append(
                    "Self-referential character relationship skipped."
                )
                continue

            relation_type = relationship.relationship_type

            # Normalize symmetric relationships so that
            # duplicates in opposite directions are detected.
            if relation_type in cls.SYMMETRIC_RELATIONS:
                dedup_key = (
                    relation_type,
                    *sorted([source_id, target_id]),
                )
                directed = False
            else:
                dedup_key = (
                    relation_type,
                    source_id,
                    target_id,
                )
                directed = True

            if dedup_key in seen_relationships:
                continue

            seen_relationships.add(dedup_key)

            edge_id = cls._make_id(
                project_id,
                "relationship",
                "|".join(map(str, dedup_key)),
            )

            edges.append(
                GraphEdge(
                    id=edge_id,
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=relation_type,
                    directed=directed,
                    confidence=relationship.confidence,
                    evidence=[
                        item.quote
                        for item in relationship.evidence
                    ],
                    properties={
                        "description": relationship.description,
                    },
                )
            )

        # ------------------------------------------------
        # 3. Create event nodes.
        # ------------------------------------------------

        event_ids = {}

        for event in events.events:

            event_id = f"event:{event.event_id}"

            if event_id in event_ids.values():
                warnings.append(
                    f"Duplicate event ID: {event.event_id}"
                )
                continue

            event_ids[event.event_id] = event_id

            nodes.append(
                GraphNode(
                    id=event_id,
                    node_type="event",
                    label=event.title,
                    properties={
                        "description": event.description,
                        "chapter_number": event.chapter_number,
                        "sequence_index": event.sequence_index,
                        "time_reference": event.time_reference,
                        "chronology_basis": event.chronology_basis,
                    },
                )
            )

            # --------------------------------------------
            # 4. Connect characters to their events.
            # --------------------------------------------

            for participant in event.participants:

                participant_id = alias_lookup.get(
                    cls._normalize(participant)
                )

                if participant_id is None:
                    warnings.append(
                        f"Unknown event participant: {participant}"
                    )
                    continue

                participation_id = cls._make_id(
                    project_id,
                    "participation",
                    f"{participant_id}:{event_id}",
                )

                edges.append(
                    GraphEdge(
                        id=participation_id,
                        source_id=participant_id,
                        target_id=event_id,
                        edge_type="PARTICIPATED_IN",
                        directed=True,
                        evidence=[
                            item.quote for item in event.evidence
                        ],
                    )
                )

            # --------------------------------------------
            # 5. Create location nodes and event links.
            # --------------------------------------------

            if event.location:

                normalized_location = cls._normalize(
                    event.location
                )

                location_id = cls._make_id(
                    project_id,
                    "location",
                    normalized_location,
                )

                existing_location = any(
                    node.id == location_id for node in nodes
                )

                if not existing_location:
                    nodes.append(
                        GraphNode(
                            id=location_id,
                            node_type="location",
                            label=event.location,
                        )
                    )

                occurred_at_id = cls._make_id(
                    project_id,
                    "occurred_at",
                    f"{event_id}:{location_id}",
                )

                edges.append(
                    GraphEdge(
                        id=occurred_at_id,
                        source_id=event_id,
                        target_id=location_id,
                        edge_type="OCCURRED_AT",
                        directed=True,
                        evidence=[
                            item.quote for item in event.evidence
                        ],
                    )
                )

        return StoryKnowledgeGraph(
            project_id=project_id,
            nodes=nodes,
            edges=edges,
            approval_status="pending",
            validation_warnings=warnings,
        )
