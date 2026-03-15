"""Tests for embedding pipeline (mocked embedder)."""

from unittest.mock import MagicMock
from uuid import uuid4

import chromadb

from mindspace.core.models import Capture, CaptureType, Stream, ThoughtContent
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB


def _make_pipeline(tmp_data_dir):
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
