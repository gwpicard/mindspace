"""Embedding pipeline — embed captures and store in vector DB."""

from mindspace.capture import store
from mindspace.core.models import Capture
from mindspace.derived.chunker import Chunker
from mindspace.derived.registry import DerivationRegistry
from mindspace.derived.text_prep import prepare_text
from mindspace.infra.config import get_settings
from mindspace.infra.embedder import Embedder
from mindspace.infra.keyword_index import KeywordIndex
from mindspace.infra.vectordb import VectorDB


class EmbeddingPipeline:
    """Embeds captures and stores them in the vector database."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        vectordb: VectorDB | None = None,
        registry: DerivationRegistry | None = None,
        keyword_index: KeywordIndex | None = None,
    ) -> None:
        self._embedder = embedder or Embedder()
        self._vectordb = vectordb or VectorDB()
        self._registry = registry or DerivationRegistry()
        self._keyword_index = keyword_index
        self._chunker = Chunker()

    def _get_keyword_index(self) -> KeywordIndex | None:
        """Lazy-load keyword index if hybrid search is enabled."""
        settings = get_settings()
        if not settings.hybrid_search_enabled:
            return None
        if self._keyword_index is None:
            self._keyword_index = KeywordIndex()
            self._keyword_index.load()
        return self._keyword_index

    def _get_parent_capture(self, capture: Capture) -> Capture | None:
        """Load parent capture for reactions."""
        from mindspace.core.models import CaptureType, ReactionContent

        if capture.type == CaptureType.reaction and isinstance(capture.content, ReactionContent):
            try:
                return store.load(capture.content.reacting_to)
            except FileNotFoundError:
                return None
        return None

    def embed_capture(self, capture: Capture, force: bool = False) -> bool:
        """Embed a single capture. Returns True if embedded, False if skipped."""
        if not force and self._registry.is_embedded(capture.id):
            return False

        parent = self._get_parent_capture(capture)
        text = prepare_text(capture, parent)
        if not text.strip():
            return False

        chunks = self._chunker.chunk(text, capture.id)

        chunk_ids = [c.chunk_id for c in chunks]
        chunk_texts = [c.text for c in chunks]
        embeddings = [self._embedder.embed_one(ct) for ct in chunk_texts]

        metadata = {
            "type": capture.type.value,
            "stream": capture.stream.value,
            "created_at": capture.created_at.isoformat(),
            "tags": ",".join(capture.context.tags),
            "capture_id": capture.id,
        }

        self._vectordb.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=[metadata for _ in chunks],
        )

        # Update keyword index
        ki = self._get_keyword_index()
        if ki is not None:
            for chunk_id, chunk_text in zip(chunk_ids, chunk_texts):
                ki.add(chunk_id, chunk_text)
            ki.save()

        self._registry.mark_embedded(capture.id)
        return True

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Search with optional hybrid (semantic + BM25 via RRF).

        Returns list of {id, document, distance, metadata} deduplicated by capture_id.
        """
        # Fetch more results than needed to allow dedup
        fetch_n = n_results * 3

        # Semantic search
        embedding = self._embedder.embed_one(query)
        raw_results = self._vectordb.query(embedding, n_results=fetch_n)

        semantic_ranked: list[tuple[str, float, str, dict]] = []
        if raw_results["ids"] and raw_results["ids"][0]:
            for i, chunk_id in enumerate(raw_results["ids"][0]):
                semantic_ranked.append((
                    chunk_id,
                    raw_results["distances"][0][i],
                    raw_results["documents"][0][i],
                    raw_results["metadatas"][0][i] if raw_results["metadatas"] else {},
                ))

        # Hybrid search with RRF
        ki = self._get_keyword_index()
        if ki is not None:
            bm25_results = ki.search(query, n_results=fetch_n)
            hits = self._rrf_fuse(semantic_ranked, bm25_results, n_results)
        else:
            hits = self._deduplicate_semantic(semantic_ranked, n_results)

        return hits

    def _deduplicate_semantic(
        self,
        ranked: list[tuple[str, float, str, dict]],
        n_results: int,
    ) -> list[dict]:
        """Deduplicate chunks by capture_id, keeping best score."""
        seen_captures: dict[str, dict] = {}
        for chunk_id, distance, document, metadata in ranked:
            capture_id = self._chunk_id_to_capture_id(chunk_id)
            if capture_id not in seen_captures or distance < seen_captures[capture_id]["distance"]:
                seen_captures[capture_id] = {
                    "id": capture_id,
                    "document": document,
                    "distance": distance,
                    "metadata": metadata,
                }

        results = sorted(seen_captures.values(), key=lambda x: x["distance"])
        return results[:n_results]

    def _rrf_fuse(
        self,
        semantic_ranked: list[tuple[str, float, str, dict]],
        bm25_ranked: list[tuple[str, float]],
        n_results: int,
        rrf_k: int = 60,
    ) -> list[dict]:
        """Reciprocal Rank Fusion of semantic and BM25 results."""
        # RRF score = sum(1 / (k + rank)) across retrieval methods
        chunk_scores: dict[str, float] = {}
        chunk_data: dict[str, tuple[str, dict]] = {}

        # Semantic RRF scores
        for rank, (chunk_id, distance, document, metadata) in enumerate(semantic_ranked):
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)
            if chunk_id not in chunk_data:
                chunk_data[chunk_id] = (document, metadata)

        # BM25 RRF scores
        for rank, (chunk_id, _score) in enumerate(bm25_ranked):
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)
            # chunk_data may not have this chunk if it wasn't in semantic results
            # We don't have the document/metadata from BM25, skip if not in semantic

        # Sort by RRF score descending
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)

        # Deduplicate by capture_id
        seen_captures: set[str] = set()
        results: list[dict] = []
        for chunk_id, rrf_score in sorted_chunks:
            capture_id = self._chunk_id_to_capture_id(chunk_id)
            if capture_id in seen_captures:
                continue
            seen_captures.add(capture_id)

            if chunk_id in chunk_data:
                document, metadata = chunk_data[chunk_id]
            else:
                # BM25-only result without document data — skip
                continue

            results.append({
                "id": capture_id,
                "document": document,
                "distance": 1.0 - rrf_score,  # Convert to distance-like metric
                "metadata": metadata,
            })
            if len(results) >= n_results:
                break

        return results

    @staticmethod
    def _chunk_id_to_capture_id(chunk_id: str) -> str:
        """Extract capture_id from chunk_id format '{capture_id}__chunk_{N}'."""
        if "__chunk_" in chunk_id:
            return chunk_id.rsplit("__chunk_", 1)[0]
        return chunk_id
