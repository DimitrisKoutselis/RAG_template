import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.application.interfaces.chunking_strategy import IChunkingStrategy
from src.domain.entities.chunk import Chunk
from src.domain.entities.document import Document
from src.domain.value_objects.chunk_metadata import ChunkMetadata


class FileBasedChunkingStrategy(IChunkingStrategy):
    """
    Chunking strategy that treats each .txt file in a chunks directory as a separate chunk.

    This strategy reads all .txt files from a specified directory and creates
    one chunk per file, associating them with the document being processed.
    """

    def __init__(self, chunks_directory: str = "./chunks") -> None:
        self._chunks_directory = Path(chunks_directory)

    @property
    def strategy_name(self) -> str:
        """Return the name of this chunking strategy."""
        return "file_based"

    async def chunk_document(self, document: Document) -> list[Chunk]:
        """
        Create chunks from .txt files in the chunks directory.

        Each .txt file becomes a separate chunk associated with the document.
        The document's own content is ignored - only the files in the chunks
        directory are used.

        Args:
            document: The document to associate chunks with

        Returns:
            List of Chunk entities, one per .txt file found
        """
        chunks: list[Chunk] = []

        if not self._chunks_directory.exists():
            self._chunks_directory.mkdir(parents=True, exist_ok=True)
            return chunks

        txt_files = sorted(self._chunks_directory.glob("*.txt"))

        current_position = 0
        for index, txt_file in enumerate(txt_files):
            content = txt_file.read_text(encoding="utf-8").strip()

            if not content:
                continue

            content_length = len(content)

            metadata = ChunkMetadata(
                chunk_index=index,
                start_position=current_position,
                end_position=current_position + content_length,
                overlap_with_previous=0,
                overlap_with_next=0
            )

            chunk = Chunk(
                id=uuid4(),
                document_id=document.id,
                content=content,
                metadata=metadata
            )

            chunks.append(chunk)
            current_position += content_length

        return chunks

    def get_config(self) -> dict[str, Any]:
        """Return the current configuration of this strategy."""
        return {
            "strategy_name": self.strategy_name,
            "chunks_directory": str(self._chunks_directory),
            "file_pattern": "*.txt"
        }
