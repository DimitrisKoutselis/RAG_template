from datetime import datetime
from uuid import uuid4

from src.application.dtos.document_dtos import (
    CreateDocumentDTO,
    DocumentResponseDTO,
)
from src.application.dtos.ingestion_dtos import IngestDocumentDTO
from src.domain.entities.document import Document
from src.domain.value_objects.document_metadata import DocumentMetadata


class DocumentMapper:
    """Mapper for document entities and DTOs."""

    @staticmethod
    def to_response_dto(
        document: Document,
        chunk_count: int
    ) -> DocumentResponseDTO:
        """Convert a document entity to a response DTO."""
        return DocumentResponseDTO(
            id=str(document.id),
            content=document.content,
            source=document.metadata.source,
            file_type=document.metadata.file_type,
            created_at=document.created_at.isoformat(),
            chunk_count=chunk_count,
            additional_metadata=document.metadata.additional_metadata
        )

    @staticmethod
    def from_create_dto(dto: CreateDocumentDTO) -> Document:
        """Convert a create DTO to a document entity."""
        now = datetime.utcnow()
        return Document(
            id=uuid4(),
            content=dto.content,
            metadata=DocumentMetadata(
                source=dto.source,
                file_type=dto.file_type,
                created_at=now,
                additional_metadata=dto.additional_metadata
            ),
            created_at=now
        )

    @staticmethod
    def from_ingest_dto(dto: IngestDocumentDTO) -> Document:
        """Convert an ingest DTO to a document entity."""
        now = datetime.utcnow()
        return Document(
            id=uuid4(),
            content=dto.content,
            metadata=DocumentMetadata(
                source=dto.source,
                file_type=dto.file_type,
                created_at=now,
                additional_metadata=dto.metadata
            ),
            created_at=now
        )
