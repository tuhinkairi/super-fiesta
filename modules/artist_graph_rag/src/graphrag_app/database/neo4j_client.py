
from typing import Any, Callable, TypeVar

from neo4j import Driver, GraphDatabase, ManagedTransaction

from graphrag_app.config import settings


T = TypeVar("T")


class Neo4jClient:
    """Manages connections, queries, and transactions for Neo4j AuraDB."""

    def __init__(self):
        self._driver: Driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_username,
                settings.neo4j_password,
            ),
        )

        self.database = settings.neo4j_database

    def verify_connection(self) -> bool:
        """Verify connectivity to the Neo4j database."""

        self._driver.verify_connectivity()
        return True

    def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query using a managed session."""

        with self._driver.session(
            database=self.database
        ) as session:
            result = session.run(query, parameters or {})
            return result.data()

    def execute_transaction(
        self,
        work: Callable[[ManagedTransaction], T],
    ) -> T:
        """Execute multiple database operations atomically."""

        with self._driver.session(
            database=self.database
        ) as session:
            return session.execute_write(work)

    def close(self) -> None:
        """Close the Neo4j driver."""

        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
