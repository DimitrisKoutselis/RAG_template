from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DocumentMetadata:
    """Immutable value object representing document metadata."""

    source: str
    file_type: str
    created_at: datetime
    additional_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("Document source cannot be empty")
        if not self.file_type:
            raise ValueError("Document file_type cannot be empty")
