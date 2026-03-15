"""Embedding pipeline — embed captures and store in vector DB."""

from mindspace.core.models import Capture
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.embedder import Embedder
from mindspace.infra.vectordb import VectorDB


class EmbeddingPipeline:
    """Embeds captures and stores them in the vector database."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        vectordb: VectorDB | None = None,
        registry: DerivationRegistry | None = None,
    ) -> None:
        self._embedder = embedder or Embedder()
        self._vectordb = vectordb or VectorDB()
        self._registry = registry or DerivationRegistry()

    def embed_capture(self, capture: Capture, force: bool = False) -> bool:
        """Embed a single capture. Returns True if embedded, False if skipped."""
        if not force and self._registry.is_embedded(capture.id):
            return False

        text = capture.text_for_embedding()
        if not text.strip():
            return False

        embedding = self._embedder.embed_one(text)
        self._vectordb.upsert(
            ids=[capture.id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "type": capture.type.value,
                "stream": capture.stream.value,
                "created_at": capture.created_at.isoformat(),
                "tags": ",".join(capture.context.tags),
            }],
        )
        self._registry.mark_embedded(capture.id)
        return True

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Semantic search. Returns list of {id, document, distance, metadata}."""
        embedding = self._embedder.embed_one(query)
        results = self._vectordb.query(embedding, n_results=n_results)

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, capture_id in enumerate(results["ids"][0]):
                hits.append({
                    "id": capture_id,
                    "document": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })
        return hits
