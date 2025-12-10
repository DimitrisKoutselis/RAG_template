from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.presentation.api.controllers.chat_controller import ChatController
from src.presentation.api.schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Controller factory - will be set by main.py during app initialization
_controller_factory: callable = None


def set_chat_controller_factory(factory: callable) -> None:
    """Set the controller factory function."""
    global _controller_factory
    _controller_factory = factory


def get_chat_controller() -> ChatController:
    """Dependency injection for chat controller."""
    if _controller_factory is None:
        raise NotImplementedError("Chat controller not configured")
    return _controller_factory()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Send a chat message and get a RAG-enhanced response.

    Optionally provide a conversation_id to continue an existing conversation.
    """
    return await controller.chat(request)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Stream a chat response using Server-Sent Events.

    The response includes retrieval results followed by streamed tokens.
    """
    async def event_generator():
        async for chunk in controller.chat_stream(request):
            yield f"data: {chunk.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
