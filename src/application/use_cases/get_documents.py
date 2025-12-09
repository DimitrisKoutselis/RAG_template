from src.application.dtos.document_dtos import DocumentResponseDTO
from src.application.mappers.document_mapper import DocumentMapper
from src.domain.repositories.chunk_repository import IChunkRepository
from src.domain.repositories.document_repository import IDocumentRepository


class GetDocumentsUseCase:
    """Use case for retrieving documents."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        chunk_repository: IChunkRepository
    ) -> None:
        self._document_repo = document_repository
        self._chunk_repo = chunk_repository

    async def execute(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[DocumentResponseDTO]:
        """Get all documents with pagination."""
        documents = await self._document_repo.get_all(
            limit=limit,
            offset=offset
        )

        result = []
        for doc in documents:
            chunks = await self._chunk_repo.get_by_document_id(doc.id)
            result.append(
                DocumentMapper.to_response_dto(doc, len(chunks))
            )

        return result
