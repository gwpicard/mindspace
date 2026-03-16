# Mindspace Evaluation System

## Overview

The eval system measures retrieval quality so you can improve it systematically. It follows Hamel Husain's philosophy: **you can't improve what you can't measure**. Every change to retrieval (chunking, hybrid search, text enrichment) should be measured before/after using this framework.

The system is built around a **golden dataset** — a hand-curated set of queries with known-good expected results from your actual corpus. This is intentionally domain-specific rather than using generic eval frameworks.

## Architecture

```
eval/
├── types.py      # Pydantic models (EvalCase, EvalDataset, EvalResult, etc.)
├── metrics.py    # Pure metric functions (no mindspace imports)
├── runner.py     # EvalRunner — runs cases against EmbeddingPipeline
└── history.py    # JSONL persistence for eval run history
```

The `eval/` layer sits between `derived/` and `cli/` in the dependency hierarchy:
```
cli/ → eval/ → derived/, infra/, core/
```

## Key Concepts

### Golden Dataset

A JSON file (`data/eval/golden.json`) containing evaluation cases. Each case is a query with expected results:

```json
{
  "version": 1,
  "cases": [
    {
      "query": "machine learning architectures",
      "expected_ids": ["01ABC..."],
      "negative_ids": ["01XYZ..."],
      "notes": "Should find the transformer paper capture"
    }
  ]
}
```

- **expected_ids**: Capture IDs that SHOULD appear in top-k results
- **negative_ids**: Capture IDs that should NOT appear (optional)
- **notes**: Human context for why this case exists

### Metrics

All metrics are pure functions in `eval/metrics.py`:

| Metric | What it measures |
|--------|-----------------|
| **Precision@k** | Fraction of top-k results that are relevant |
| **Recall@k** | Fraction of relevant items found in top-k |
| **MRR** | 1/rank of the first relevant result (Mean Reciprocal Rank) |
| **Hit@k** | Binary: did ANY relevant result appear in top-k? |
| **Negative Leakage** | Which negative IDs leaked into top-k results |

### Pass/Fail

A case **passes** if any expected capture appears in the top-k results (hit@k = True). The overall **pass rate** equals the hit rate across all cases.

### Eval History

Every `ms eval run` appends a full result (all metrics + config snapshot) to `data/eval/history.jsonl`. This creates a timeline you can use to track improvement or regression.

The config snapshot records: embedding model, dimensions, chunk settings, and hybrid search flag — so you know exactly what configuration produced each result.

## CLI Commands

### `ms eval run`

Run all golden dataset cases and print a summary.

```bash
ms eval run              # Default: k=5
ms eval run --k 10       # Use top-10
ms eval run --verbose    # Show per-case PASS/FAIL details
```

Output:
```
Eval Results  (k=5, 8 cases)
  Pass rate:    88%
  Hit rate:     88%
  Mean MRR:     0.750
  Mean P@5:     0.425
  Mean R@5:     0.875
```

Results are automatically saved to history.

### `ms eval history`

Show a table of all past runs.

```bash
ms eval history
```

Output:
```
┌─────────────────────┬───┬───────┬───────────┬───────┬───────┬───────┐
│ Timestamp           │ k │ Cases │ Pass Rate │ MRR   │ P@k   │ R@k   │
├─────────────────────┼───┼───────┼───────────┼───────┼───────┼───────┤
│ 2026-03-15T10:30:00 │ 5 │ 8     │ 75%       │ 0.625 │ 0.350 │ 0.750 │
│ 2026-03-15T11:45:00 │ 5 │ 8     │ 88%       │ 0.750 │ 0.425 │ 0.875 │
└─────────────────────┴───┴───────┴───────────┴───────┴───────┴───────┘
```

### `ms eval compare`

Compare the last two runs with color-coded deltas.

```bash
ms eval compare
```

Output:
```
Comparing
  Before: 2026-03-15T10:30:00
  After:  2026-03-15T11:45:00

  precision_at_k       +0.075
  recall_at_k          +0.125
  mrr                  +0.125
  hit_rate             +0.125
  pass_rate            +0.125
```

Green = improvement, red = regression.

### `ms eval add-case`

Interactive workflow to create a new eval case:

```bash
ms eval add-case
```

1. Prompts for a search query
2. Runs the query and displays results with IDs and scores
3. Asks you to mark which results are relevant (by index)
4. Optionally mark which should NOT appear
5. Appends the case to `data/eval/golden.json`

This is the primary tool for curating your golden dataset.

### `ms eval golden`

List all cases in the current golden dataset.

```bash
ms eval golden
```

## Workflow: Improving Retrieval

The standard workflow for any retrieval change:

```bash
# 1. Baseline
ms eval run                    # Record current state

# 2. Make the change
# (edit config, code, etc.)

# 3. Reindex with new settings
ms admin reindex

# 4. Measure
ms eval run                    # Record new state

# 5. Compare
ms eval compare                # See the deltas
```

Example scenarios:
- **Enable chunking**: Change `chunk_max_tokens` in config → reindex → eval
- **Toggle hybrid search**: Set `hybrid_search_enabled` → reindex → eval
- **Adjust chunk overlap**: Change `chunk_overlap_tokens` → reindex → eval

## Retrieval Improvements (Stage 1.5)

Three retrieval improvements were built and measured with this framework:

### 1. Text Chunking

Long captures (e.g., 3000-word articles) are split into overlapping chunks for more precise embedding. Configuration:

- `MINDSPACE_CHUNK_MAX_TOKENS` (default: 500) — max words per chunk
- `MINDSPACE_CHUNK_OVERLAP_TOKENS` (default: 50) — overlap between chunks

Split priority: paragraph boundaries (`\n\n`) → sentence (`. `) → word boundary.

Each chunk gets its own vector in ChromaDB with ID format `{capture_id}__chunk_{N}`. Search results are deduplicated back to capture IDs, keeping the best-scoring chunk.

### 2. Hybrid Search (BM25 + Semantic)

Combines semantic similarity (embeddings) with keyword matching (BM25) using **Reciprocal Rank Fusion (RRF)**.

- BM25 index is built from chunk texts, persisted to `data/derived/bm25_corpus.json`
- RRF combines rankings: `score = Σ 1/(k + rank)` across both methods (k=60)
- RRF is rank-based (no score scale issues), parameter-free, and robust
- Toggle: `MINDSPACE_HYBRID_SEARCH_ENABLED` (default: True)

### 3. Text Enrichment

Before embedding, text is enriched based on capture type:

- **URL captures**: `Title: {title}\nTags: {tags}\n\n{extracted_text}`
- **Reactions**: `Reacting to: {parent_text[:200]}\nStance: {stance}\n\n{text}`
- **Others**: Used as-is (thoughts, questions, snippets are already concise)

## Configuration

All settings via environment variables or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MINDSPACE_CHUNK_MAX_TOKENS` | 500 | Max words per chunk |
| `MINDSPACE_CHUNK_OVERLAP_TOKENS` | 50 | Word overlap between chunks |
| `MINDSPACE_HYBRID_SEARCH_ENABLED` | True | Enable BM25 + semantic fusion |

## Data Files

| Path | Format | Description |
|------|--------|-------------|
| `data/eval/golden.json` | JSON | Golden evaluation dataset |
| `data/eval/history.jsonl` | JSONL | Append-only eval run history |
| `data/derived/bm25_corpus.json` | JSON | Persisted BM25 keyword index |

## Testing

```bash
# Run all tests (65 passing)
.venv/bin/python -m pytest tests/

# Eval-specific tests
.venv/bin/python -m pytest tests/eval/ -v

# Chunker tests
.venv/bin/python -m pytest tests/derived/test_chunker.py -v
```

Test files:
- `tests/eval/test_metrics.py` — Pure metric function tests (30 tests)
- `tests/eval/test_runner.py` — Runner with mocked pipeline (5 tests)
- `tests/eval/test_retrieval_quality.py` — Regression tests with deterministic embedder
- `tests/derived/test_chunker.py` — Chunking logic tests (6 tests)
- `tests/eval/fixtures/golden_test.json` — Synthetic golden dataset for tests

## Future (Stage 2)

When Claude API integration lands in Stage 2, the eval framework extends to:

- **RAG Triad**: Context Relevance (measured now) + Groundedness + Answer Relevance
- **HyDE**: LLM generates hypothetical answer, embed that instead of query
- **Re-ranking**: Claude re-orders top results by relevance
- **LLM-as-judge**: Claude critiques retrieval quality at scale
