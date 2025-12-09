from dataclasses import dataclass


@dataclass(frozen=True)
class Embedding:
    """Immutable value object representing a vector embedding."""

    vector: tuple[float, ...]
    model_name: str
    dimensions: int

    def __post_init__(self) -> None:
        if not self.vector:
            raise ValueError("Embedding vector cannot be empty")
        if len(self.vector) != self.dimensions:
            raise ValueError(
                f"Vector length ({len(self.vector)}) does not match "
                f"dimensions ({self.dimensions})"
            )
        if not self.model_name:
            raise ValueError("model_name cannot be empty")

    @classmethod
    def from_list(
        cls,
        vector: list[float],
        model_name: str
    ) -> "Embedding":
        """Create an Embedding from a list of floats."""
        return cls(
            vector=tuple(vector),
            model_name=model_name,
            dimensions=len(vector)
        )

    def to_list(self) -> list[float]:
        """Convert the embedding vector to a list."""
        return list(self.vector)
