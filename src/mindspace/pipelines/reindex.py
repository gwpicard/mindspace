"""Reindex pipeline — wipe derived data and re-derive from raw captures."""

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.config import get_settings
from mindspace.infra.keyword_index import KeywordIndex
from mindspace.infra.vectordb import VectorDB


def reindex(
    pipeline: EmbeddingPipeline | None = None,
    vectordb: VectorDB | None = None,
    registry: DerivationRegistry | None = None,
) -> dict:
    """Wipe all derived data and re-embed all captures from raw.

    Returns stats dict with counts.
    """
    vectordb = vectordb or VectorDB()
    registry = registry or DerivationRegistry()

    # Wipe derived
    vectordb.delete_all()
    registry.clear()

    # Clear keyword index
    settings = get_settings()
    keyword_index = None
    if settings.hybrid_search_enabled:
        keyword_index = KeywordIndex()
        keyword_index.clear()

    # Re-derive
    pipeline = pipeline or EmbeddingPipeline(
        vectordb=vectordb,
        registry=registry,
        keyword_index=keyword_index,
    )
    captures = store.iterate_all()
    embedded = 0
    skipped = 0

    for capture in captures:
        if pipeline.embed_capture(capture, force=True):
            embedded += 1
        else:
            skipped += 1

    return {
        "total": len(captures),
        "embedded": embedded,
        "skipped": skipped,
    }
