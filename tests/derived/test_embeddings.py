"""Tests for embedding pipeline (mocked embedder)."""

from unittest.mock import MagicMock
from uuid import uuid4

import chromadb

from mindspace.core.models import Capture, CaptureType, Stream, ThoughtContent
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.keyword_index import KeywordIndex
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB


def _make_pipeline(tmp_data_dir, keyword_index=None):
    ensure_dirs()
    mock_embedder = MagicMock()
    mock_embedder.embed_one.return_value = [0.1] * 1536
    mock_embedder.embed.return_value = [[0.1] * 1536]

    client = chromadb.Client()
    vectordb = VectorDB(client=client, collection_name=f"test-{uuid4()}")
    registry = DerivationRegistry()

    pipeline = EmbeddingPipeline(
        embedder=mock_embedder,
        vectordb=vectordb,
        registry=registry,
        keyword_index=keyword_index,
    )
    return pipeline, mock_embedder, vectordb, registry


def test_embed_capture(tmp_data_dir):
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Deep thought about AI"),
    )

    result = pipeline.embed_capture(capture)
    assert result is True
    assert registry.is_embedded(capture.id)
    assert vectordb.count() == 1
    mock_embedder.embed_one.assert_called_once_with("Deep thought about AI")


def test_embed_capture_skips_if_already_embedded(tmp_data_dir):
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Another thought"),
    )

    pipeline.embed_capture(capture)
    result = pipeline.embed_capture(capture)
    assert result is False
    assert mock_embedder.embed_one.call_count == 1


def test_embed_capture_force(tmp_data_dir):
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Forced thought"),
    )

    pipeline.embed_capture(capture)
    result = pipeline.embed_capture(capture, force=True)
    assert result is True
    assert mock_embedder.embed_one.call_count == 2


def test_search(tmp_data_dir):
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Machine learning is transformative"),
    )
    pipeline.embed_capture(capture)

    results = pipeline.search("AI and ML")
    assert len(results) == 1
    assert results[0]["id"] == capture.id


def test_search_hybrid_rrf_ranking(tmp_data_dir):
    """Hybrid search returns results with distances in valid cosine range (0–2)."""
    ki = KeywordIndex()
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir, keyword_index=ki)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Research on artificial intelligence"),
    )
    pipeline.embed_capture(capture)

    results = pipeline.search("research")
    assert len(results) == 1
    assert results[0]["id"] == capture.id
    # Distance should be in valid cosine distance range [0, 2], not RRF-derived ~0.97
    # Small negative values possible from floating point in ChromaDB
    assert -1e-4 <= results[0]["distance"] <= 2.0


def test_search_hybrid_scores_use_cosine_distance(tmp_data_dir):
    """Hybrid search distance field contains real cosine distance, not RRF score."""
    ki = KeywordIndex()
    pipeline, mock_embedder, vectordb, registry = _make_pipeline(tmp_data_dir, keyword_index=ki)

    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=ThoughtContent(text="Deep learning neural networks"),
    )
    pipeline.embed_capture(capture)

    # Get semantic-only distance for comparison
    semantic_results = pipeline._deduplicate_semantic(
        [(f"{capture.id}__chunk_0", d, doc, meta)
         for d, doc, meta in [(
             pipeline._vectordb.query(
                 mock_embedder.embed_one("neural networks"), n_results=1
             )["distances"][0][0],
             "Deep learning neural networks",
             {},
         )]],
        n_results=1,
    )
    semantic_distance = semantic_results[0]["distance"]

    # Hybrid search should use the same cosine distance
    hybrid_results = pipeline.search("neural networks")
    assert len(hybrid_results) == 1
    assert hybrid_results[0]["distance"] == semantic_distance
