"""Evaluation runner — executes eval cases against the embedding pipeline."""

from datetime import datetime, timezone

from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.eval.metrics import (
    hit_at_k,
    mrr,
    negative_leakage,
    precision_at_k,
    recall_at_k,
)
from mindspace.eval.types import CaseResult, EvalCase, EvalDataset, EvalResult, EvalSummary
from mindspace.infra.config import get_settings


class EvalRunner:
    """Runs evaluation cases against an EmbeddingPipeline."""

    def __init__(self, pipeline: EmbeddingPipeline) -> None:
        self._pipeline = pipeline

    def _run_case(self, case: EvalCase, k: int) -> CaseResult:
        """Run a single evaluation case."""
        results = self._pipeline.search(case.query, n_results=k)
        retrieved_ids = [r["id"] for r in results]

        return CaseResult(
            case=case,
            retrieved_ids=retrieved_ids,
            precision_at_k=precision_at_k(retrieved_ids, case.expected_ids, k),
            recall_at_k=recall_at_k(retrieved_ids, case.expected_ids, k),
            mrr=mrr(retrieved_ids, case.expected_ids),
            hit=hit_at_k(retrieved_ids, case.expected_ids, k),
            leaked_negatives=negative_leakage(retrieved_ids, case.negative_ids, k),
        )

    def _snapshot_config(self) -> dict:
        """Capture current config for reproducibility."""
        settings = get_settings()
        return {
            "embedding_model": settings.embedding_model,
            "embedding_dimensions": settings.embedding_dimensions,
            "chunk_max_tokens": settings.chunk_max_tokens,
            "chunk_overlap_tokens": settings.chunk_overlap_tokens,
            "hybrid_search_enabled": settings.hybrid_search_enabled,
        }

    def run(self, dataset: EvalDataset, k: int = 5) -> EvalResult:
        """Run all cases in the dataset and compute aggregate metrics."""
        per_case = [self._run_case(case, k) for case in dataset.cases]

        if per_case:
            mean_p = sum(c.precision_at_k for c in per_case) / len(per_case)
            mean_r = sum(c.recall_at_k for c in per_case) / len(per_case)
            mean_m = sum(c.mrr for c in per_case) / len(per_case)
            hits = sum(1 for c in per_case if c.hit)
            hit_rate = hits / len(per_case)
        else:
            mean_p = mean_r = mean_m = hit_rate = 0.0

        summary = EvalSummary(
            mean_precision_at_k=mean_p,
            mean_recall_at_k=mean_r,
            mean_mrr=mean_m,
            hit_rate=hit_rate,
            num_cases=len(per_case),
            pass_rate=hit_rate,
        )

        return EvalResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            config_snapshot=self._snapshot_config(),
            k=k,
            per_case=per_case,
            summary=summary,
        )
