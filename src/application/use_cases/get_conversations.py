from src.application.dtos.conversation_dtos import ConversationResponseDTO
from src.application.mappers.conversation_mapper import ConversationMapper
from src.domain.repositories.conversation_repository import IConversationRepository


class GetConversationsUseCase:
    """Use case for retrieving conversations."""

    def __init__(
        self,
        conversation_repository: IConversationRepository
    ) -> None:
        self._conversation_repo = conversation_repository

    async def execute(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[ConversationResponseDTO]:
        """Get all conversations with pagination."""
        conversations = await self._conversation_repo.get_all(
            limit=limit,
            offset=offset
        )

        return [
            ConversationMapper.to_response_dto(conv)
            for conv in conversations
        ]
