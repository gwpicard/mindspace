"""Tests for evaluation runner."""

from unittest.mock import MagicMock
from uuid import uuid4

import chromadb

from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.eval.runner import EvalRunner
from mindspace.eval.types import EvalCase, EvalDataset
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB


def _make_pipeline(tmp_data_dir):
    ensure_dirs()
    mock_embedder = MagicMock()
    mock_embedder.embed_one.return_value = [0.1] * 1536

    client = chromadb.Client()
    vectordb = VectorDB(client=client, collection_name=f"test-{uuid4()}")
    registry = DerivationRegistry()

    pipeline = EmbeddingPipeline(
        embedder=mock_embedder,
        vectordb=vectordb,
        registry=registry,
        keyword_index=None,
    )
    return pipeline, mock_embedder, vectordb


def test_run_empty_dataset(tmp_data_dir):
    pipeline, _, _ = _make_pipeline(tmp_data_dir)
    runner = EvalRunner(pipeline)
    dataset = EvalDataset(cases=[])
    result = runner.run(dataset, k=5)
    assert result.summary.num_cases == 0
    assert result.summary.hit_rate == 0.0


def test_run_with_hit(tmp_data_dir):
    pipeline, mock_embedder, vectordb = _make_pipeline(tmp_data_dir)

    # Insert a document directly
    vectordb.upsert(
        ids=["cap_001__chunk_0"],
        embeddings=[[0.1] * 1536],
        documents=["test document about AI"],
        metadatas=[{"type": "thought", "stream": "internal", "created_at": "", "tags": "", "capture_id": "cap_001"}],
    )

    case = EvalCase(query="AI research", expected_ids=["cap_001"])
    dataset = EvalDataset(cases=[case])

    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=5)

    assert result.summary.num_cases == 1
    assert result.summary.hit_rate == 1.0
    assert result.per_case[0].hit is True
    assert result.per_case[0].precision_at_k == 1.0
    assert result.per_case[0].recall_at_k == 1.0


def test_run_with_miss(tmp_data_dir):
    pipeline, _, vectordb = _make_pipeline(tmp_data_dir)

    # Insert a document that won't match expected
    vectordb.upsert(
        ids=["cap_002__chunk_0"],
        embeddings=[[0.1] * 1536],
        documents=["cooking recipe"],
        metadatas=[{"type": "thought", "stream": "internal", "created_at": "", "tags": "", "capture_id": "cap_002"}],
    )

    case = EvalCase(query="cooking", expected_ids=["cap_999"])
    dataset = EvalDataset(cases=[case])

    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=5)

    assert result.summary.hit_rate == 0.0
    assert result.per_case[0].hit is False


def test_run_negative_leakage(tmp_data_dir):
    pipeline, _, vectordb = _make_pipeline(tmp_data_dir)

    vectordb.upsert(
        ids=["cap_bad__chunk_0"],
        embeddings=[[0.1] * 1536],
        documents=["irrelevant result"],
        metadatas=[{"type": "thought", "stream": "internal", "created_at": "", "tags": "", "capture_id": "cap_bad"}],
    )

    case = EvalCase(
        query="test",
        expected_ids=["cap_good"],
        negative_ids=["cap_bad"],
    )
    dataset = EvalDataset(cases=[case])

    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=5)

    assert "cap_bad" in result.per_case[0].leaked_negatives


def test_config_snapshot(tmp_data_dir):
    pipeline, _, _ = _make_pipeline(tmp_data_dir)
    runner = EvalRunner(pipeline)
    dataset = EvalDataset(cases=[])
    result = runner.run(dataset)
    assert "embedding_model" in result.config_snapshot
    assert "chunk_max_tokens" in result.config_snapshot
    assert "hybrid_search_enabled" in result.config_snapshot
