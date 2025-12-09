from collections.abc import AsyncIterator

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.application.interfaces.llm_provider import ILLMProvider
from src.domain.entities.message import Message
from src.domain.exceptions.domain_exceptions import LLMGenerationException
from src.domain.value_objects.message_role import MessageRole
from src.infrastructure.configuration.settings import Settings


class LangChainLLMProvider(ILLMProvider):
    """LangChain-based LLM provider implementation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI | ChatAnthropic:
        """Create the LangChain LLM instance based on settings."""
        if self._settings.llm_provider == "openai":
            return ChatOpenAI(
                model=self._settings.llm_model,
                temperature=self._settings.llm_temperature,
                max_tokens=self._settings.llm_max_tokens,
                api_key=self._settings.openai_api_key
            )
        elif self._settings.llm_provider == "anthropic":
            return ChatAnthropic(
                model=self._settings.llm_model,
                temperature=self._settings.llm_temperature,
                max_tokens=self._settings.llm_max_tokens,
                api_key=self._settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self._settings.llm_provider}")

    def _build_messages(
        self,
        prompt: str,
        context: str | None = None,
        conversation_history: list[Message] | None = None,
        system_prompt: str | None = None
    ) -> list:
        """Build LangChain messages from inputs."""
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        if conversation_history:
            for msg in conversation_history:
                if msg.role == MessageRole.USER:
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(AIMessage(content=msg.content))
                elif msg.role == MessageRole.SYSTEM:
                    messages.append(SystemMessage(content=msg.content))

        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt

        messages.append(HumanMessage(content=full_prompt))

        return messages

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
        try:
            messages = self._build_messages(
                prompt, context, conversation_history, system_prompt
            )

            llm = self._llm
            if temperature != self._settings.llm_temperature:
                llm = llm.with_config(configurable={"temperature": temperature})

            response = await llm.ainvoke(messages)
            return response.content

        except Exception as e:
            raise LLMGenerationException(f"Failed to generate response: {e}") from e

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
        try:
            messages = self._build_messages(
                prompt, context, conversation_history, system_prompt
            )

            async for chunk in self._llm.astream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            raise LLMGenerationException(f"Failed to generate response: {e}") from e
