from typing import Any

from pydantic import BaseModel, Field


class CreateDocumentRequest(BaseModel):
    """Request schema for creating a document."""

    content: str = Field(..., min_length=1, description="Document content")
    source: str = Field(..., min_length=1, description="Document source (e.g., file path, URL)")
    file_type: str = Field(..., min_length=1, description="Document file type (e.g., txt, pdf, md)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentResponse(BaseModel):
    """Response schema for a document."""

    id: str
    content: str
    source: str
    file_type: str
    created_at: str
    chunk_count: int
    metadata: dict[str, Any]


class DocumentListResponse(BaseModel):
    """Response schema for document list."""

    documents: list[DocumentResponse]
    total: int
