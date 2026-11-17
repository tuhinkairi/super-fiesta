from graphrag_app.graph import (
    Entity,
    Relationship,
    GraphService,
    GraphMapper,
    GraphIngestionService,
)


def test_graph_package_exports():
    """Verify that all public graph components are available."""

    assert Entity is not None
    assert Relationship is not None
    assert GraphService is not None
    assert GraphMapper is not None
    assert GraphIngestionService is not None


def test_entity_can_be_created():
    """Verify that Entity is accessible through the package."""

    entity = Entity(
        name="Python",
        entity_type="Programming Language",
    )

    assert entity.name == "Python"
    assert entity.entity_type == "Programming Language"


def test_relationship_can_be_created():
    """Verify that Relationship is accessible through the package."""

    relationship = Relationship(
        source_entity_id="entity-001",
        target_entity_id="entity-002",
        relation_type="USED_FOR",
    )

    assert relationship.source_entity_id == "entity-001"
    assert relationship.target_entity_id == "entity-002"
    assert relationship.relation_type == "USED_FOR"
