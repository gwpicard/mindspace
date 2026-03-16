"""Eval history persistence — JSONL append log of evaluation runs."""

import json

from mindspace.eval.types import EvalResult
from mindspace.infra.paths import eval_history_path


def save_run(result: EvalResult) -> None:
    """Append an eval run to history."""
    path = eval_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(result.model_dump_json() + "\n")


def load_history() -> list[EvalResult]:
    """Load all eval runs from history."""
    path = eval_history_path()
    if not path.exists():
        return []
    runs = []
    for line in path.read_text().strip().split("\n"):
        if line.strip():
            runs.append(EvalResult.model_validate_json(line))
    return runs


def compare_runs(a: EvalResult, b: EvalResult) -> dict:
    """Compare two runs and return metric deltas (b - a)."""
    return {
        "precision_at_k": b.summary.mean_precision_at_k - a.summary.mean_precision_at_k,
        "recall_at_k": b.summary.mean_recall_at_k - a.summary.mean_recall_at_k,
        "mrr": b.summary.mean_mrr - a.summary.mean_mrr,
        "hit_rate": b.summary.hit_rate - a.summary.hit_rate,
        "pass_rate": b.summary.pass_rate - a.summary.pass_rate,
    }
