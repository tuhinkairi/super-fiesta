"""Data models for dense and sparse embeddings."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class DenseEmbedding:
    """Represents a dense vector embedding."""

    values: list[float]
    model: str
    dimension: int = field(init=False)

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("Dense embedding cannot be empty.")

        if not self.model.strip():
            raise ValueError("Embedding model name cannot be empty.")

        if any(not isinstance(value, (int, float)) for value in self.values):
            raise TypeError("Dense embedding values must be numeric.")

        self.values = [float(value) for value in self.values]
        self.dimension = len(self.values)


@dataclass(slots=True)
class SparseEmbedding:
    """Represents a sparse vector embedding."""

    indices: list[int]
    values: list[float]
    model: str

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("Sparse embedding model name cannot be empty.")

        if len(self.indices) != len(self.values):
            raise ValueError(
                "Sparse indices and values must have equal lengths."
            )

        if any(not isinstance(index, int) or isinstance(index, bool) or index < 0
               for index in self.indices):
            raise ValueError("Sparse indices must be non-negative integers.")

        if any(not isinstance(value, (int, float)) for value in self.values):
            raise TypeError("Sparse embedding values must be numeric.")

        if any(not isinstance(value, (int, float)) for value in self.values):
            raise TypeError("Sparse embedding values must be numeric.")

        self.values = [float(value) for value in self.values]

        if len(set(self.indices)) != len(self.indices):
            raise ValueError("Sparse embedding indices must be unique.")
