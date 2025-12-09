from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.presentation.api.controllers.chat_controller import ChatController
from src.presentation.api.schemas.chat_schemas import ChatRequest

router = APIRouter(tags=["WebSocket"])


def get_chat_controller() -> ChatController:
    """Dependency injection placeholder for chat controller."""
    raise NotImplementedError("Chat controller not configured")


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
):
    """
    WebSocket endpoint for real-time chat.

    Send JSON messages with the ChatRequest schema.
    Receive streaming responses as JSON chunks.
    """
    await websocket.accept()

    controller: ChatController = websocket.app.state.chat_controller

    try:
        while True:
            data = await websocket.receive_json()

            try:
                request = ChatRequest(**data)

                async for chunk in controller.chat_stream(request):
                    await websocket.send_json(chunk.model_dump())

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": str(e)
                })

    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()
