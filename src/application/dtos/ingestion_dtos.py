from dataclasses import dataclass, field
from typing import Any


@dataclass
class IngestDocumentDTO:
    """DTO for document ingestion request."""

    content: str
    source: str
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResultDTO:
    """DTO for document ingestion result."""

    document_id: str
    chunk_count: int
    success: bool
    error_message: str | None = None
