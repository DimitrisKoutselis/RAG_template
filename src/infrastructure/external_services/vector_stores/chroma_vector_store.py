from typing import Any
from uuid import UUID

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.application.interfaces.vector_store import IVectorStore
from src.domain.entities.chunk import Chunk
from src.domain.entities.retrieval_result import RetrievalResult
from src.domain.exceptions.domain_exceptions import RetrievalException
from src.domain.value_objects.chunk_metadata import ChunkMetadata
from src.domain.value_objects.embedding import Embedding
from src.infrastructure.configuration.settings import Settings


class ChromaVectorStore(IVectorStore):
    """ChromaDB vector store implementation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings to the vector store."""
        if not chunks:
            return

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            if not chunk.has_embedding():
                raise ValueError(f"Chunk {chunk.id} does not have an embedding")

            ids.append(str(chunk.id))
            embeddings.append(chunk.embedding.to_list())
            documents.append(chunk.content)
            metadatas.append({
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.metadata.chunk_index,
                "start_position": chunk.metadata.start_position,
                "end_position": chunk.metadata.end_position,
            })

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    async def search(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[RetrievalResult]:
        """Search for similar chunks."""
        try:
            where_filter = None
            if filter_metadata:
                where_filter = filter_metadata

            results = self._collection.query(
                query_embeddings=[query_embedding.to_list()],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances", "embeddings"]
            )

            retrieval_results = []

            if results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 0
                    similarity_score = 1 - distance

                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    content = results["documents"][0][i] if results["documents"] else ""

                    chunk = Chunk(
                        id=UUID(chunk_id),
                        document_id=UUID(metadata.get("document_id", chunk_id)),
                        content=content,
                        metadata=ChunkMetadata(
                            chunk_index=metadata.get("chunk_index", 0),
                            start_position=metadata.get("start_position", 0),
                            end_position=metadata.get("end_position", len(content)),
                        ),
                        embedding=None
                    )

                    retrieval_results.append(
                        RetrievalResult(
                            chunk=chunk,
                            similarity_score=max(0.0, min(1.0, similarity_score)),
                            rank=i + 1
                        )
                    )

            return retrieval_results

        except Exception as e:
            raise RetrievalException(f"Failed to search vector store: {e}") from e

    async def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a document."""
        try:
            results = self._collection.get(
                where={"document_id": str(document_id)},
                include=[]
            )

            if results["ids"]:
                self._collection.delete(ids=results["ids"])
                return len(results["ids"])

            return 0

        except Exception as e:
            raise RetrievalException(
                f"Failed to delete from vector store: {e}"
            ) from e

    async def delete_all(self) -> None:
        """Delete all chunks from the vector store."""
        self._client.delete_collection(self._settings.chroma_collection_name)
        self._collection = self._client.create_collection(
            name=self._settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store collection."""
        return {
            "name": self._collection.name,
            "count": self._collection.count(),
            "metadata": self._collection.metadata
        }
