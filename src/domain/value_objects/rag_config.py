from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RAGConfig:
    """Immutable configuration for RAG operations."""

    top_k: int = 5
    similarity_threshold: float = 0.7
    include_metadata: bool = True
    implementation: Literal["langchain", "langgraph"] = "langchain"

    def __post_init__(self) -> None:
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        if self.implementation not in ("langchain", "langgraph"):
            raise ValueError("implementation must be 'langchain' or 'langgraph'")
