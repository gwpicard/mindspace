"""Evaluation types for retrieval quality measurement."""

from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    """A single evaluation case: query + expected results."""

    query: str
    expected_ids: list[str]
    negative_ids: list[str] = Field(default_factory=list)
    notes: str = ""


class EvalDataset(BaseModel):
    """Collection of evaluation cases."""

    version: int = 1
    cases: list[EvalCase] = Field(default_factory=list)


class CaseResult(BaseModel):
    """Result of running a single evaluation case."""

    case: EvalCase
    retrieved_ids: list[str]
    precision_at_k: float
    recall_at_k: float
    mrr: float
    hit: bool
    leaked_negatives: list[str] = Field(default_factory=list)


class EvalSummary(BaseModel):
    """Aggregate metrics across all cases."""

    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_mrr: float
    hit_rate: float
    num_cases: int
    pass_rate: float


class EvalResult(BaseModel):
    """Full result of an evaluation run."""

    timestamp: str
    config_snapshot: dict
    k: int
    per_case: list[CaseResult]
    summary: EvalSummary
