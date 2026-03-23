"""Unified search across conversations and resources."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.web.db.models import Conversation, Message, Resource

logger = logging.getLogger(__name__)


class SearchService:
    """Hybrid search across both ChromaDB collections, merged via RRF."""

    def __init__(self) -> None:
        from mindspace.infra.embedder import Embedder

        self._embedder = Embedder()

    async def search(
        self,
        query: str,
        db: AsyncSession,
        n_results: int = 10,
        channel_ids: list[str] | None = None,
        types: list[str] | None = None,
    ) -> list[dict]:
        """Search across captures and conversation_chunks collections."""
        embedding = await asyncio.to_thread(self._embedder.embed_one, query)

        # Query both collections in parallel
        captures_task = asyncio.to_thread(self._query_collection, "captures", embedding, n_results * 2)
        convos_task = asyncio.to_thread(self._query_collection, "conversation_chunks", embedding, n_results * 2)

        captures_raw, convos_raw = await asyncio.gather(captures_task, convos_task)

        # Parse into ranked lists
        captures_ranked = self._parse_results(captures_raw, "capture")
        convos_ranked = self._parse_results(convos_raw, "conversation")

        # RRF fusion across both collections
        fused = self._rrf_fuse(captures_ranked, convos_ranked, n_results)

        # Enrich with DB data
        enriched = await self._enrich_results(fused, db)

        return enriched

    def _query_collection(self, collection_name: str, embedding: list[float], n: int) -> dict:
        from mindspace.infra.vectordb import VectorDB

        try:
            vdb = VectorDB(collection_name=collection_name)
            if vdb.count() == 0:
                return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
            return vdb.query(embedding, n_results=min(n, vdb.count()))
        except Exception:
            logger.exception("Failed to query collection %s", collection_name)
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    def _parse_results(
        self, raw: dict, source: str
    ) -> list[tuple[str, float, str, dict, str]]:
        """Parse ChromaDB results into (id, distance, document, metadata, source) tuples."""
        results = []
        if not raw["ids"] or not raw["ids"][0]:
            return results
        for i, chunk_id in enumerate(raw["ids"][0]):
            results.append((
                chunk_id,
                raw["distances"][0][i],
                raw["documents"][0][i],
                raw["metadatas"][0][i] if raw["metadatas"] else {},
                source,
            ))
        return results

    def _rrf_fuse(
        self,
        list_a: list[tuple[str, float, str, dict, str]],
        list_b: list[tuple[str, float, str, dict, str]],
        n_results: int,
        rrf_k: int = 60,
    ) -> list[dict]:
        """RRF fusion of two ranked lists, deduplicated by source_id."""
        scores: dict[str, float] = {}
        data: dict[str, dict] = {}

        for rank, (chunk_id, distance, document, metadata, source) in enumerate(list_a):
            source_id = self._extract_source_id(chunk_id, metadata, source)
            scores[source_id] = scores.get(source_id, 0) + 1.0 / (rrf_k + rank + 1)
            if source_id not in data:
                data[source_id] = {
                    "id": source_id,
                    "document": document,
                    "distance": distance,
                    "metadata": metadata,
                    "source": source,
                }

        for rank, (chunk_id, distance, document, metadata, source) in enumerate(list_b):
            source_id = self._extract_source_id(chunk_id, metadata, source)
            scores[source_id] = scores.get(source_id, 0) + 1.0 / (rrf_k + rank + 1)
            if source_id not in data:
                data[source_id] = {
                    "id": source_id,
                    "document": document,
                    "distance": distance,
                    "metadata": metadata,
                    "source": source,
                }

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        return [data[sid] for sid in sorted_ids[:n_results] if sid in data]

    def _extract_source_id(self, chunk_id: str, metadata: dict, source: str) -> str:
        """Extract a meaningful source ID for dedup."""
        if "__chunk_" in chunk_id:
            base = chunk_id.rsplit("__chunk_", 1)[0]
        else:
            base = chunk_id

        # For conversation chunks, dedup by conversation_id
        if source == "conversation" and metadata.get("conversation_id"):
            return f"conv:{metadata['conversation_id']}"

        # For captures, dedup by capture_id
        if metadata.get("capture_id"):
            return f"capture:{metadata['capture_id']}"

        return f"{source}:{base}"

    async def _enrich_results(self, results: list[dict], db: AsyncSession) -> list[dict]:
        """Add conversation/resource context from the database."""
        enriched = []
        for r in results:
            entry = {
                "snippet": r["document"][:300],
                "distance": r["distance"],
                "source": r["source"],
                "metadata": r["metadata"],
            }

            if r["source"] == "conversation":
                conv_id = r["metadata"].get("conversation_id", "")
                conv = await db.get(Conversation, conv_id) if conv_id else None
                entry["conversation_id"] = conv_id
                entry["conversation_title"] = conv.title if conv else None
                entry["type"] = "message"
            else:
                capture_id = r["metadata"].get("capture_id", "")
                entry["capture_id"] = capture_id
                entry["type"] = r["metadata"].get("type", "unknown")
                entry["title"] = r["metadata"].get("title") or r["metadata"].get("tags", "")

            enriched.append(entry)
        return enriched
