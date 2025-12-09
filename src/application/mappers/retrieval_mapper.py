from src.application.dtos.chat_dtos import RetrievalResultDTO
from src.domain.entities.retrieval_result import RetrievalResult


class RetrievalMapper:
    """Mapper for retrieval result entities and DTOs."""

    @staticmethod
    def to_dto(result: RetrievalResult) -> RetrievalResultDTO:
        """Convert a retrieval result entity to a DTO."""
        return RetrievalResultDTO(
            chunk_id=str(result.chunk.id),
            content=result.chunk.content,
            document_id=str(result.chunk.document_id),
            similarity_score=result.similarity_score,
            rank=result.rank
        )

    @staticmethod
    def to_dtos(results: list[RetrievalResult]) -> list[RetrievalResultDTO]:
        """Convert a list of retrieval result entities to DTOs."""
        return [RetrievalMapper.to_dto(r) for r in results]
