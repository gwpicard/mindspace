"""ChromaDB adapter for vector storage and search."""

import chromadb

from mindspace.infra.paths import chroma_dir


COLLECTION_NAME = "captures"


class VectorDB:
    """Wraps ChromaDB for storing and querying capture embeddings."""

    def __init__(self, client: chromadb.ClientAPI | None = None, collection_name: str = COLLECTION_NAME) -> None:
        self._client = client or chromadb.PersistentClient(path=str(chroma_dir()))
        self._collection_name = collection_name
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict] | None = None,
    ) -> None:
        """Add or update vectors."""
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
    ) -> dict:
        """Query for similar vectors. Returns ChromaDB results dict."""
        return self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    def count(self) -> int:
        """Return the number of stored vectors."""
        return self._collection.count()

    def delete_all(self) -> None:
        """Delete the collection and recreate it."""
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
