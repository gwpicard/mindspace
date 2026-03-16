"""Pure metric functions for retrieval evaluation. No mindspace imports."""


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of top-k retrieved that are relevant."""
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant_ids)
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / len(top_k)


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of relevant items that appear in top-k retrieved."""
    if not relevant_ids or k <= 0:
        return 0.0
    top_k = set(retrieved_ids[:k])
    hits = sum(1 for rid in relevant_ids if rid in top_k)
    return hits / len(relevant_ids)


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """Mean Reciprocal Rank: 1/rank of first relevant result."""
    relevant_set = set(relevant_ids)
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def hit_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> bool:
    """Whether any relevant item appears in top-k."""
    if k <= 0:
        return False
    relevant_set = set(relevant_ids)
    return any(rid in relevant_set for rid in retrieved_ids[:k])


def negative_leakage(retrieved_ids: list[str], negative_ids: list[str], k: int) -> list[str]:
    """Return negative IDs that leaked into top-k results."""
    if k <= 0 or not negative_ids:
        return []
    top_k = set(retrieved_ids[:k])
    negative_set = set(negative_ids)
    return [rid for rid in retrieved_ids[:k] if rid in negative_set]
