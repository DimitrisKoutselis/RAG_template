from uuid import UUID

from src.application.interfaces.vector_store import IVectorStore
from src.domain.exceptions.domain_exceptions import DocumentNotFoundException
from src.domain.repositories.chunk_repository import IChunkRepository
from src.domain.repositories.document_repository import IDocumentRepository


class DeleteDocumentUseCase:
    """Use case for deleting a document and its chunks."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        chunk_repository: IChunkRepository,
        vector_store: IVectorStore
    ) -> None:
        self._document_repo = document_repository
        self._chunk_repo = chunk_repository
        self._vector_store = vector_store

    async def execute(self, document_id: str) -> bool:
        """
        Delete a document and all its associated chunks.

        Steps:
        1. Verify document exists
        2. Delete from vector store
        3. Delete chunks from repository
        4. Delete document from repository
        """
        doc_uuid = UUID(document_id)

        document = await self._document_repo.get_by_id(doc_uuid)
        if not document:
            raise DocumentNotFoundException(doc_uuid)

        await self._vector_store.delete_by_document_id(doc_uuid)

        await self._chunk_repo.delete_by_document_id(doc_uuid)

        return await self._document_repo.delete(doc_uuid)
