import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.domain.exceptions.domain_exceptions import (
    ChunkNotFoundException,
    ChunkingException,
    ConversationNotFoundException,
    DocumentNotFoundException,
    DomainException,
    EmbeddingGenerationException,
    InvalidDocumentException,
    LLMGenerationException,
    MessageNotFoundException,
    RetrievalException,
)

logger = logging.getLogger("rag_template.middleware")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and converting to HTTP responses."""

    async def dispatch(self, request: Request, call_next):
        """Handle request and catch exceptions."""
        try:
            return await call_next(request)

        except DocumentNotFoundException as e:
            logger.warning(f"Document not found: {e.document_id}")
            return JSONResponse(
                status_code=404,
                content={"error": str(e), "type": "document_not_found"}
            )

        except ConversationNotFoundException as e:
            logger.warning(f"Conversation not found: {e.conversation_id}")
            return JSONResponse(
                status_code=404,
                content={"error": str(e), "type": "conversation_not_found"}
            )

        except ChunkNotFoundException as e:
            logger.warning(f"Chunk not found: {e.chunk_id}")
            return JSONResponse(
                status_code=404,
                content={"error": str(e), "type": "chunk_not_found"}
            )

        except MessageNotFoundException as e:
            logger.warning(f"Message not found: {e.message_id}")
            return JSONResponse(
                status_code=404,
                content={"error": str(e), "type": "message_not_found"}
            )

        except InvalidDocumentException as e:
            logger.warning(f"Invalid document: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": str(e), "type": "invalid_document"}
            )

        except ChunkingException as e:
            logger.error(f"Chunking error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": "chunking_error"}
            )

        except EmbeddingGenerationException as e:
            logger.error(f"Embedding generation error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": "embedding_error"}
            )

        except RetrievalException as e:
            logger.error(f"Retrieval error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": "retrieval_error"}
            )

        except LLMGenerationException as e:
            logger.error(f"LLM generation error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": "llm_error"}
            )

        except DomainException as e:
            logger.error(f"Domain error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": "domain_error"}
            )

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": str(e), "type": "validation_error"}
            )

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "type": "internal_error"}
            )
