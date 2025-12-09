from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "RAG Template"
    app_version: str = "0.1.0"
    debug: bool = False

    rag_implementation: Literal["langchain", "langgraph"] = "langchain"

    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    embedding_provider: Literal["openai"] = "openai"
    embedding_model: str = "text-embedding-3-small"

    vector_store_provider: Literal["chroma"] = "chroma"
    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "rag_chunks"

    database_url: str = "sqlite+aiosqlite:///./data/rag.db"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]

    default_top_k: int = 5
    default_similarity_threshold: float = 0.7

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
