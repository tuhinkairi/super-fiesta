"""Resource registration and cleanup utilities."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class ResourceCleanupError(RuntimeError):
    """Raised when one or more resource cleanup operations fail."""

    def __init__(self, errors: list[Exception]) -> None:
        self.errors = tuple(errors)
        super().__init__(
            f"{len(errors)} resource cleanup operation(s) failed."
        )


@dataclass(frozen=True, slots=True)
class ResourceRegistration:
    """Information about a registered resource."""

    token: int
    resource_name: str


@dataclass(slots=True)
class _ResourceEntry:
    token: int
    resource: Any
    cleanup: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    resource_name: str


class ResourceRegistry:
    """Register resources and clean them up in reverse registration order."""

    def __init__(self) -> None:
        self._resources: list[_ResourceEntry] = []
        self._next_token = 1
        self._lock = threading.RLock()
        self._closed = False

    def register(
        self,
        resource: Any,
        *,
        cleanup: Callable[..., Any] | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        name: str | None = None,
    ) -> ResourceRegistration:
        """Register a resource and its cleanup operation."""

        if resource is None:
            raise ValueError("resource cannot be None.")

        if not isinstance(args, tuple):
            raise TypeError("args must be a tuple.")

        if kwargs is not None and not isinstance(kwargs, dict):
            raise TypeError("kwargs must be a dictionary.")

        cleanup_function = cleanup or getattr(resource, "close", None)

        if not callable(cleanup_function):
            raise ValueError(
                "Resource must provide a callable close method "
                "or an explicit cleanup callback."
            )

        resource_name = name or type(resource).__name__

        if not isinstance(resource_name, str) or not resource_name.strip():
            raise ValueError("Resource name must be a non-empty string.")

        with self._lock:
            if self._closed:
                raise RuntimeError("Resource registry is already closed.")

            token = self._next_token
            self._next_token += 1

            self._resources.append(
                _ResourceEntry(
                    token=token,
                    resource=resource,
                    cleanup=cleanup_function,
                    args=args,
                    kwargs=dict(kwargs or {}),
                    resource_name=resource_name,
                )
            )

            return ResourceRegistration(
                token=token,
                resource_name=resource_name,
            )

    def release(self, token: int) -> bool:
        """Clean up and unregister one resource."""

        if isinstance(token, bool) or not isinstance(token, int):
            raise TypeError("token must be an integer.")

        with self._lock:
            entry = next(
                (item for item in self._resources if item.token == token),
                None,
            )

            if entry is None:
                return False

            self._resources.remove(entry)

        entry.cleanup(*entry.args, **entry.kwargs)
        return True

    def close_all(self, *, raise_errors: bool = True) -> int:
        """Clean up all resources in reverse registration order."""

        if not isinstance(raise_errors, bool):
            raise TypeError("raise_errors must be a boolean.")

        with self._lock:
            if self._closed:
                return 0

            self._closed = True
            entries = list(reversed(self._resources))
            self._resources.clear()

        errors: list[Exception] = []

        for entry in entries:
            try:
                entry.cleanup(*entry.args, **entry.kwargs)
            except Exception as exc:
                errors.append(
                    RuntimeError(
                        f"Failed to clean up {entry.resource_name}: {exc}"
                    )
                )

        if errors and raise_errors:
            raise ResourceCleanupError(errors)

        return len(entries)

    def get_registered_resources(self) -> list[ResourceRegistration]:
        """Return information about currently registered resources."""

        with self._lock:
            return [
                ResourceRegistration(
                    token=entry.token,
                    resource_name=entry.resource_name,
                )
                for entry in self._resources
            ]

    def contains(self, token: int) -> bool:
        """Check whether a resource token is registered."""

        with self._lock:
            return any(entry.token == token for entry in self._resources)

    @property
    def resource_count(self) -> int:
        with self._lock:
            return len(self._resources)

    @property
    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def __enter__(self) -> ResourceRegistry:
        if self.is_closed:
            raise RuntimeError("Cannot enter a closed resource registry.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> bool:
        try:
            self.close_all()
        except ResourceCleanupError as cleanup_error:
            if exc_value is not None:
                raise ExceptionGroup(
                    "The operation and resource cleanup both failed.",
                    [exc_value, cleanup_error],
                )
            raise

        return False


def register_resource(
    registry: ResourceRegistry,
    resource: Any,
    *,
    cleanup: Callable[..., Any] | None = None,
    name: str | None = None,
) -> ResourceRegistration:
    """Convenience function for registering a resource."""

    if not isinstance(registry, ResourceRegistry):
        raise TypeError("registry must be a ResourceRegistry.")

    return registry.register(
        resource,
        cleanup=cleanup,
        name=name,
    )


__all__ = [
    "ResourceCleanupError",
    "ResourceRegistration",
    "ResourceRegistry",
    "register_resource",
]
