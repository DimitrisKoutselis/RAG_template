from collections.abc import AsyncIterator

from src.application.dtos.ingestion_dtos import IngestDocumentDTO
from src.application.use_cases.delete_document import DeleteDocumentUseCase
from src.application.use_cases.get_documents import GetDocumentsUseCase
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.presentation.api.schemas.document_schemas import (
    CreateDocumentRequest,
    DocumentListResponse,
    DocumentResponse,
)


class DocumentController:
    """Controller for document operations."""

    def __init__(
        self,
        ingest_use_case: IngestDocumentUseCase,
        delete_use_case: DeleteDocumentUseCase,
        get_documents_use_case: GetDocumentsUseCase
    ) -> None:
        self._ingest = ingest_use_case
        self._delete = delete_use_case
        self._get_documents = get_documents_use_case

    async def ingest_document(
        self,
        request: CreateDocumentRequest
    ) -> DocumentResponse:
        """Ingest a new document."""
        dto = IngestDocumentDTO(
            content=request.content,
            source=request.source,
            file_type=request.file_type,
            metadata=request.metadata
        )

        result = await self._ingest.execute(dto)

        if not result.success:
            raise ValueError(result.error_message or "Failed to ingest document")

        return DocumentResponse(
            id=result.document_id,
            content=request.content,
            source=request.source,
            file_type=request.file_type,
            created_at="",  # Will be set by mapper in actual implementation
            chunk_count=result.chunk_count,
            metadata=request.metadata
        )

    async def delete_document(self, document_id: str) -> dict:
        """Delete a document."""
        await self._delete.execute(document_id)
        return {"success": True, "message": f"Document {document_id} deleted"}

    async def list_documents(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> DocumentListResponse:
        """List all documents."""
        documents = await self._get_documents.execute(limit=limit, offset=offset)

        return DocumentListResponse(
            documents=[
                DocumentResponse(
                    id=doc.id,
                    content=doc.content,
                    source=doc.source,
                    file_type=doc.file_type,
                    created_at=doc.created_at,
                    chunk_count=doc.chunk_count,
                    metadata=doc.additional_metadata
                )
                for doc in documents
            ],
            total=len(documents)
        )
