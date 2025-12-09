from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkMetadata:
    """Immutable value object representing chunk metadata."""

    chunk_index: int
    start_position: int
    end_position: int
    overlap_with_previous: int = 0
    overlap_with_next: int = 0

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")
        if self.start_position < 0:
            raise ValueError("start_position must be non-negative")
        if self.end_position < self.start_position:
            raise ValueError("end_position must be >= start_position")
        if self.overlap_with_previous < 0:
            raise ValueError("overlap_with_previous must be non-negative")
        if self.overlap_with_next < 0:
            raise ValueError("overlap_with_next must be non-negative")

    @property
    def length(self) -> int:
        """Return the length of the chunk in characters."""
        return self.end_position - self.start_position
