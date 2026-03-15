"""Reindex pipeline — wipe derived data and re-derive from raw captures."""

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
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

    # Re-derive
    pipeline = pipeline or EmbeddingPipeline(vectordb=vectordb, registry=registry)
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
