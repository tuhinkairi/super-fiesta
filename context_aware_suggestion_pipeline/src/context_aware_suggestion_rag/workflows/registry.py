"""
Workflow registry.

Stores and manages workflow definitions independently
from executable workflow implementations.
"""

from __future__ import annotations

from threading import RLock

from context_aware_suggestion_rag.exceptions import WorkflowError
from context_aware_suggestion_rag.workflows.models import WorkflowDefinition


class WorkflowRegistry:
    """Thread-safe registry for workflow definitions."""

    def __init__(self) -> None:
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._lock = RLock()

    def register(
        self,
        definition: WorkflowDefinition,
        *,
        replace: bool = False,
    ) -> None:
        """Register a workflow definition."""

        if not isinstance(definition, WorkflowDefinition):
            raise TypeError(
                "Expected a WorkflowDefinition instance."
            )

        name = definition.name.strip()

        with self._lock:
            if name in self._definitions and not replace:
                raise WorkflowError(
                    f"Workflow definition '{name}' already exists."
                )

            self._definitions[name] = definition

    def get(self, name: str) -> WorkflowDefinition:
        """Retrieve a workflow definition."""

        normalized_name = self._validate_name(name)

        with self._lock:
            definition = self._definitions.get(normalized_name)

            if definition is None:
                raise WorkflowError(
                    f"Workflow definition '{normalized_name}' not found."
                )

            return definition

    def exists(self, name: str) -> bool:
        """Check whether a definition exists."""

        normalized_name = self._validate_name(name)

        with self._lock:
            return normalized_name in self._definitions

    def unregister(self, name: str) -> bool:
        """Remove a workflow definition."""

        normalized_name = self._validate_name(name)

        with self._lock:
            return (
                self._definitions.pop(normalized_name, None)
                is not None
            )

    def list_names(self) -> tuple[str, ...]:
        """Return all registered definition names."""

        with self._lock:
            return tuple(self._definitions.keys())

    def list_definitions(
        self,
        *,
        enabled_only: bool = False,
    ) -> tuple[WorkflowDefinition, ...]:
        """Return registered workflow definitions."""

        if not isinstance(enabled_only, bool):
            raise TypeError("enabled_only must be a boolean.")

        with self._lock:
            definitions = tuple(self._definitions.values())

        if enabled_only:
            return tuple(
                definition
                for definition in definitions
                if definition.enabled
            )

        return definitions

    def clear(self) -> None:
        """Remove all registered definitions."""

        with self._lock:
            self._definitions.clear()

    def __len__(self) -> int:
        """Return the number of registered definitions."""

        with self._lock:
            return len(self._definitions)

    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate and normalize a workflow name."""

        if not isinstance(name, str):
            raise TypeError("Workflow name must be a string.")

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Workflow name cannot be empty.")

        return normalized_name
