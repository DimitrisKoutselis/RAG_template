from fastapi import APIRouter, Depends, Query

from src.presentation.api.controllers.conversation_controller import ConversationController
from src.presentation.api.schemas.conversation_schemas import (
    ConversationHistoryResponse,
    ConversationListResponse,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# Controller factory - will be set by main.py during app initialization
_controller_factory: callable = None


def set_conversation_controller_factory(factory: callable) -> None:
    """Set the controller factory function."""
    global _controller_factory
    _controller_factory = factory


def get_conversation_controller() -> ConversationController:
    """Dependency injection for conversation controller."""
    if _controller_factory is None:
        raise NotImplementedError("Conversation controller not configured")
    return _controller_factory()


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    controller: ConversationController = Depends(get_conversation_controller)
):
    """List all conversations."""
    return await controller.get_conversations(limit=limit, offset=offset)


@router.get("/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation(
    conversation_id: str,
    controller: ConversationController = Depends(get_conversation_controller)
):
    """Get a conversation with its message history."""
    return await controller.get_conversation_history(conversation_id)
