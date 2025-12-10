from fastapi import APIRouter, Depends, Query

from src.presentation.api.controllers.document_controller import DocumentController
from src.presentation.api.schemas.document_schemas import (
    CreateDocumentRequest,
    DocumentListResponse,
    DocumentResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])

# Controller factory - will be set by main.py during app initialization
_controller_factory: callable = None


def set_document_controller_factory(factory: callable) -> None:
    """Set the controller factory function."""
    global _controller_factory
    _controller_factory = factory


def get_document_controller() -> DocumentController:
    """Dependency injection for document controller."""
    if _controller_factory is None:
        raise NotImplementedError("Document controller not configured")
    return _controller_factory()


@router.post("/", response_model=DocumentResponse, status_code=201)
async def ingest_document(
    request: CreateDocumentRequest,
    controller: DocumentController = Depends(get_document_controller)
):
    """
    Ingest a new document into the RAG system.

    The document will be chunked and embeddings will be generated.
    """
    return await controller.ingest_document(request)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    controller: DocumentController = Depends(get_document_controller)
):
    """List all documents in the RAG system."""
    return await controller.list_documents(limit=limit, offset=offset)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    controller: DocumentController = Depends(get_document_controller)
):
    """Delete a document and all its chunks from the RAG system."""
    return await controller.delete_document(document_id)
