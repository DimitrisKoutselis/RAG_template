from dataclasses import dataclass, field
from typing import Any


@dataclass
class CreateDocumentDTO:
    """DTO for creating a document."""

    content: str
    source: str
    file_type: str
    additional_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentResponseDTO:
    """DTO for document response."""

    id: str
    content: str
    source: str
    file_type: str
    created_at: str
    chunk_count: int
    additional_metadata: dict[str, Any]
