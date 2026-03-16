"""End-to-end integration test: capture → embed → search round-trip."""

from unittest.mock import MagicMock
from uuid import uuid4

import chromadb
import numpy as np

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB
from mindspace.pipelines import ingest
from mindspace.pipelines.reindex import reindex


def _make_deterministic_embedder():
    """Create a mock embedder that returns deterministic embeddings based on text content."""
    mock = MagicMock()

    def embed_one(text: str) -> list[float]:
        # Use hash to create a deterministic but varied embedding
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        # Create a 1536-dim vector from the hash
        rng = np.random.RandomState(int.from_bytes(h[:4], "big"))
        vec = rng.randn(1536).tolist()
        # Normalize
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm for x in vec]

    mock.embed_one.side_effect = embed_one
    mock.embed.side_effect = lambda texts: [embed_one(t) for t in texts]
    return mock


def test_capture_embed_search_roundtrip(tmp_data_dir):
    """Full flow: capture thoughts → embed → search → find relevant results."""
    ensure_dirs()

    embedder = _make_deterministic_embedder()
    client = chromadb.Client()
    vectordb = VectorDB(client=client, collection_name=f"test-{uuid4()}")
    registry = DerivationRegistry()
    pipeline = EmbeddingPipeline(embedder=embedder, vectordb=vectordb, registry=registry)

    # Capture several items
    c1 = ingest.ingest_thought(
        text="Large language models are changing how we write software",
        tags=["ai", "software"],
        pipeline=pipeline,
    )
    c2 = ingest.ingest_thought(
        text="The best pasta recipe uses San Marzano tomatoes",
        tags=["cooking"],
        pipeline=pipeline,
    )
    c3 = ingest.ingest_question(
        text="How will AI agents transform software development workflows?",
        tags=["ai"],
        pipeline=pipeline,
    )

    # Verify captures exist
    assert store.count() == 3
    assert vectordb.count() == 3

    # Search for AI-related content
    results = pipeline.search("artificial intelligence programming")
    assert len(results) >= 2

    # Verify we get IDs back
    result_ids = [r["id"] for r in results]
    assert c1.id in result_ids or c3.id in result_ids

    # Show a specific capture
    loaded = store.load(c1.id)
    assert loaded.content.text == "Large language models are changing how we write software"


def test_reindex_roundtrip(tmp_data_dir):
    """Capture → embed → wipe → reindex → search still works."""
    ensure_dirs()

    embedder = _make_deterministic_embedder()
    client = chromadb.Client()
    vectordb = VectorDB(client=client, collection_name=f"test-{uuid4()}")
    registry = DerivationRegistry()
    pipeline = EmbeddingPipeline(embedder=embedder, vectordb=vectordb, registry=registry)

    # Capture
    ingest.ingest_thought(text="Neural networks learn features", tags=["ml"], pipeline=pipeline)
    ingest.ingest_thought(text="Gradient descent optimizes loss", tags=["ml"], pipeline=pipeline)

    assert vectordb.count() == 2

    # Reindex (wipe + rebuild)
    stats = reindex(pipeline=pipeline, vectordb=vectordb, registry=registry)
    assert stats["total"] == 2
    assert stats["embedded"] == 2

    # Search still works after reindex
    results = pipeline.search("machine learning optimization")
    assert len(results) == 2
