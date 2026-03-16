"""Retrieval quality regression tests using deterministic mock embedder."""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
import chromadb

from mindspace.core.models import Capture, CaptureType, Stream, ThoughtContent
from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.derived.registry import DerivationRegistry
from mindspace.eval.runner import EvalRunner
from mindspace.eval.types import EvalDataset
from mindspace.infra.paths import ensure_dirs
from mindspace.infra.vectordb import VectorDB
from unittest.mock import MagicMock


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_deterministic_embedder():
    """Create a mock embedder that returns deterministic embeddings based on text content."""
    mock = MagicMock()

    def embed_one(text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).digest()
        rng = np.random.RandomState(int.from_bytes(h[:4], "big"))
        vec = rng.randn(1536).tolist()
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm for x in vec]

    mock.embed_one.side_effect = embed_one
    mock.embed.side_effect = lambda texts: [embed_one(t) for t in texts]
    return mock


def _setup_corpus(tmp_data_dir):
    """Set up a test corpus with known captures."""
    ensure_dirs()

    embedder = _make_deterministic_embedder()
    client = chromadb.Client()
    vectordb = VectorDB(client=client, collection_name=f"test-{uuid4()}")
    registry = DerivationRegistry()
    pipeline = EmbeddingPipeline(
        embedder=embedder, vectordb=vectordb, registry=registry, keyword_index=None,
    )

    captures = {
        "cap_ml_001": Capture(
            id="cap_ml_001",
            stream=Stream.internal,
            type=CaptureType.thought,
            content=ThoughtContent(text="Deep learning and neural networks are transforming machine learning research with transformer architectures"),
        ),
        "cap_cooking_001": Capture(
            id="cap_cooking_001",
            stream=Stream.internal,
            type=CaptureType.thought,
            content=ThoughtContent(text="The best pasta recipe uses San Marzano tomatoes with fresh basil and olive oil"),
        ),
        "cap_dev_001": Capture(
            id="cap_dev_001",
            stream=Stream.internal,
            type=CaptureType.thought,
            content=ThoughtContent(text="Test-driven development and continuous integration improve software development quality"),
        ),
    }

    for capture in captures.values():
        pipeline.embed_capture(capture, force=True)

    return pipeline, captures


def test_retrieval_quality_with_golden_dataset(tmp_data_dir):
    """Run the golden test dataset and verify minimum quality bar."""
    pipeline, captures = _setup_corpus(tmp_data_dir)

    golden_data = json.loads((FIXTURES_DIR / "golden_test.json").read_text())
    dataset = EvalDataset.model_validate(golden_data)

    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=3)

    # Minimum quality bar: at least 2 out of 3 cases should pass
    assert result.summary.hit_rate >= 0.66, (
        f"Hit rate {result.summary.hit_rate:.0%} below minimum 66%. "
        f"Failing cases: {[c.case.query for c in result.per_case if not c.hit]}"
    )


def test_eval_result_structure(tmp_data_dir):
    """Verify eval results have correct structure and all captures are reachable."""
    pipeline, captures = _setup_corpus(tmp_data_dir)

    golden_data = json.loads((FIXTURES_DIR / "golden_test.json").read_text())
    dataset = EvalDataset.model_validate(golden_data)

    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=5)

    # Structural checks
    assert result.summary.num_cases == 3
    assert result.k == 5
    assert len(result.per_case) == 3
    assert 0.0 <= result.summary.mean_mrr <= 1.0
    assert 0.0 <= result.summary.hit_rate <= 1.0

    # All retrieved IDs should be valid capture IDs from our corpus
    valid_ids = set(captures.keys())
    for case_result in result.per_case:
        for rid in case_result.retrieved_ids:
            assert rid in valid_ids, f"Unknown capture ID in results: {rid}"
