"""
Workflow state management.

Provides a thread-safe state container for workflow execution.
"""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any


class WorkflowState:
    """Thread-safe mutable state for a workflow execution."""

    def __init__(
        self,
        initial_data: dict[str, Any] | None = None,
    ) -> None:
        if initial_data is not None and not isinstance(initial_data, dict):
            raise TypeError("Initial workflow state must be a dictionary.")

        self._data: dict[str, Any] = deepcopy(initial_data or {})
        self._errors: list[str] = []
        self._lock = RLock()
        self._version = 0

    @property
    def version(self) -> int:
        """Return the current state version."""
        with self._lock:
            return self._version

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from workflow state."""
        self._validate_key(key)

        with self._lock:
            return deepcopy(self._data.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Set or replace a state value."""
        self._validate_key(key)

        with self._lock:
            self._data[key] = deepcopy(value)
            self._version += 1

    def update(self, values: dict[str, Any]) -> None:
        """Update multiple state values."""
        if not isinstance(values, dict):
            raise TypeError("State update must be a dictionary.")

        with self._lock:
            self._data.update(deepcopy(values))
            if values:
                self._version += 1

    def delete(self, key: str) -> bool:
        """Delete a state value."""
        self._validate_key(key)

        with self._lock:
            if key not in self._data:
                return False

            del self._data[key]
            self._version += 1
            return True

    def contains(self, key: str) -> bool:
        """Check whether a key exists."""
        self._validate_key(key)

        with self._lock:
            return key in self._data

    def add_error(self, error: str) -> None:
        """Record a workflow error."""
        if not isinstance(error, str) or not error.strip():
            raise ValueError("Workflow error cannot be empty.")

        with self._lock:
            self._errors.append(error.strip())
            self._version += 1

    def get_errors(self) -> tuple[str, ...]:
        """Return recorded workflow errors."""
        with self._lock:
            return tuple(self._errors)

    def clear_errors(self) -> None:
        """Clear recorded workflow errors."""
        with self._lock:
            if self._errors:
                self._errors.clear()
                self._version += 1

    def snapshot(self) -> dict[str, Any]:
        """Return a deep copy of the current state."""
        with self._lock:
            return deepcopy(self._data)

    def clear(self) -> None:
        """Clear state data and recorded errors."""
        with self._lock:
            if self._data or self._errors:
                self._data.clear()
                self._errors.clear()
                self._version += 1

    @staticmethod
    def _validate_key(key: str) -> None:
        """Validate a state key."""
        if not isinstance(key, str):
            raise TypeError("State key must be a string.")

        if not key.strip():
            raise ValueError("State key cannot be empty.")

    def __contains__(self, key: str) -> bool:
        return self.contains(key)

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"WorkflowState("
                f"keys={list(self._data.keys())!r}, "
                f"errors={len(self._errors)}, "
                f"version={self._version})"
            )
