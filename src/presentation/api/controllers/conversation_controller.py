from src.application.use_cases.get_conversation_history import GetConversationHistoryUseCase
from src.application.use_cases.get_conversations import GetConversationsUseCase
from src.presentation.api.schemas.conversation_schemas import (
    ConversationHistoryResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)


class ConversationController:
    """Controller for conversation operations."""

    def __init__(
        self,
        get_conversations_use_case: GetConversationsUseCase,
        get_history_use_case: GetConversationHistoryUseCase
    ) -> None:
        self._get_conversations = get_conversations_use_case
        self._get_history = get_history_use_case

    async def get_conversations(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> ConversationListResponse:
        """Get all conversations."""
        conversations = await self._get_conversations.execute(
            limit=limit,
            offset=offset
        )

        return ConversationListResponse(
            conversations=[
                ConversationResponse(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                    message_count=conv.message_count
                )
                for conv in conversations
            ],
            total=len(conversations)
        )

    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> ConversationHistoryResponse:
        """Get conversation with message history."""
        conversation, messages = await self._get_history.execute(conversation_id)

        return ConversationHistoryResponse(
            conversation=ConversationResponse(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                message_count=conversation.message_count
            ),
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                    retrieved_chunks=msg.retrieved_chunks
                )
                for msg in messages
            ]
        )
