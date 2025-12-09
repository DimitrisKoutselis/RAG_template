from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.domain.entities.message import Message


class ILLMProvider(ABC):
    """Interface for LLM providers (OpenAI, Anthropic, etc.)."""

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        conversation_history: list[Message] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Generate a response from the LLM."""
        ...

    @abstractmethod
    async def generate_response_stream(
        self,
        prompt: str,
        context: str | None = None,
        conversation_history: list[Message] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM."""
        ...
