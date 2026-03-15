"""Tests for ingest pipeline (mocked external services)."""

from unittest.mock import MagicMock, patch

import chromadb

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB
from mindspace.pipelines import ingest


def _make_pipeline(tmp_data_dir):
    ensure_dirs()
    mock_embedder = MagicMock()
    mock_embedder.embed_one.return_value = [0.1] * 1536

    client = chromadb.Client()
    vectordb = VectorDB(client=client)
    registry = DerivationRegistry()

    return EmbeddingPipeline(embedder=mock_embedder, vectordb=vectordb, registry=registry)


def test_ingest_thought(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)
    capture = ingest.ingest_thought(
        text="The future of AI is collaborative",
        thinking_type="hypothesis",
        tags=["ai"],
        pipeline=pipeline,
    )
    assert capture.type.value == "thought"
    assert capture.content.text == "The future of AI is collaborative"
    assert capture.context.tags == ["ai"]
    assert store.exists(capture.id)


def test_ingest_snippet(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)
    capture = ingest.ingest_snippet(
        text="Important quote here",
        source_description="Some article",
        tags=["quote"],
        pipeline=pipeline,
    )
    assert capture.type.value == "snippet"
    assert store.exists(capture.id)


def test_ingest_question(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)
    capture = ingest.ingest_question(
        text="What is the impact of LLMs on software?",
        domain="AI",
        urgency="active",
        tags=["research"],
        pipeline=pipeline,
    )
    assert capture.type.value == "question"
    assert capture.content.urgency.value == "active"


def test_ingest_url(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)

    with patch("mindspace.pipelines.ingest.extract_url") as mock_extract:
        mock_extract.return_value = {
            "url": "https://example.com",
            "title": "Example",
            "extracted_text": "Content here",
            "excerpt": "Content here",
            "author": None,
            "word_count": 2,
            "language": None,
            "extraction_method": "trafilatura",
            "raw_html_hash": "abc123",
        }
        capture = ingest.ingest_url("https://example.com", tags=["test"], pipeline=pipeline)

    assert capture.type.value == "url"
    assert capture.content.url == "https://example.com"
    assert store.exists(capture.id)


def test_ingest_reaction(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)

    # First create something to react to
    original = ingest.ingest_thought(text="Original thought", pipeline=pipeline)

    reaction = ingest.ingest_reaction(
        text="I disagree because...",
        reacting_to=original.id,
        stance="disagree",
        pipeline=pipeline,
    )
    assert reaction.type.value == "reaction"
    assert reaction.content.reacting_to == original.id
    assert original.id in reaction.context.related_ids


def test_ingest_reaction_invalid_id(tmp_data_dir):
    pipeline = _make_pipeline(tmp_data_dir)

    import pytest
    with pytest.raises(ValueError, match="not found"):
        ingest.ingest_reaction(
            text="Reaction",
            reacting_to="nonexistent",
            pipeline=pipeline,
        )
