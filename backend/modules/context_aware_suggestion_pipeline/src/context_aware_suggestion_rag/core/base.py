"""
Shared abstract base classes for Context-Aware Suggestion RAG.

Provides common foundations for services and components throughout
the package.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseService(ABC):
    """
    Abstract foundation for application services.

    All services should have a clear name and may implement
    initialization and cleanup operations.
    """

    def __init__(self, service_name: str) -> None:
        if not service_name.strip():
            raise ValueError("Service name cannot be empty.")

        self.service_name = service_name

    def initialize(self) -> None:
        """Initialize service resources when required."""

    def close(self) -> None:
        """Release service resources when required."""

    def __enter__(self) -> "BaseService":
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        self.close()


class BaseProcessor(ABC, Generic[InputT, OutputT]):
    """
    Abstract foundation for data-processing components.

    InputT represents the accepted input type.
    OutputT represents the produced output type.
    """

    @abstractmethod
    def process(self, data: InputT) -> OutputT:
        """Process input data and return the corresponding output."""
        ...


class BaseProvider(ABC):
    """
    Abstract foundation for external provider implementations.

    Examples include API clients, news providers and trend providers.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection with the external provider."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is available."""
        ...


class BaseRepository(ABC, Generic[InputT]):
    """
    Abstract foundation for data repositories.

    Provides a common contract for storing and retrieving data.
    """

    @abstractmethod
    def save(self, item: InputT) -> None:
        """Persist an item."""
        ...

    @abstractmethod
    def get(self, item_id: str) -> InputT | None:
        """Retrieve an item by its identifier."""
        ...

    @abstractmethod
    def delete(self, item_id: str) -> None:
        """Delete an item by its identifier."""
        ...


class BaseWorkflow(ABC, Generic[InputT, OutputT]):
    """
    Abstract foundation for workflow implementations.

    LangGraph workflows can use this abstraction when a common
    execution interface is useful.
    """

    @abstractmethod
    def execute(self, input_data: InputT) -> OutputT:
        """Execute the workflow and return its result."""
        ...


__all__ = [
    "BaseService",
    "BaseProcessor",
    "BaseProvider",
    "BaseRepository",
    "BaseWorkflow",
]
