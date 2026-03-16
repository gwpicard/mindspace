# Mindspace

A personal intelligence system that ingests what you encounter (articles, URLs) and what you think (reactions, thoughts, questions), embeds everything for semantic retrieval, and progressively layers intelligence on top — surfacing patterns, connections, and gaps in your thinking.

**Core insight:** You already have good signal detection. The bottleneck isn't finding interesting things — it's processing and connecting them over time. Mindspace closes that loop.

## What Mindspace Is Not

- Not a note-taking app (no manual organization required)
- Not a bookmarking tool (captures are processed, not just saved)
- Not a chatbot (intelligence is grounded in your actual corpus)
- Not a search engine (it knows what you've already seen and thought)

## Quick Start

```bash
# Clone
git clone https://github.com/gwpicard/mindspace.git
cd mindspace

# Set up environment
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env and add your OpenAI API key

# Initialize data directories
ms admin init

# Capture your first items
ms capture url "https://example.com/interesting-article" --tag ai --tag research
ms capture thought --text "LLMs are changing how we approach software architecture"
ms capture question "How will AI agents transform development workflows?" --domain AI

# Search across everything
ms search query "artificial intelligence"
```

## Capture Types

Mindspace organizes captures into two streams:

**External** (what you encounter):
- `ms capture url <URL>` — Fetch, extract, and embed a web page
- `ms capture snippet --text "..." --source "paper title"` — Save a text excerpt

**Internal** (what you think):
- `ms capture thought --text "..."` — Record an observation, hypothesis, or reflection
- `ms capture question "..." --domain AI` — Track open questions
- `ms capture react <CAPTURE_ID> --text "..." --stance agree` — React to any existing capture

Every capture gets a ULID, is stored as immutable JSON, and is immediately embedded for semantic search.

## Search

```bash
# Semantic search (hybrid: embeddings + BM25 keyword matching)
ms search query "machine learning optimization"

# Show more results
ms search query "cooking recipes" --num 10

# Include low-relevance matches
ms search query "vague topic" --all

# View full details of a capture
ms search show <CAPTURE_ID>
```

Search uses **Reciprocal Rank Fusion (RRF)** to combine semantic similarity (OpenAI embeddings via ChromaDB) with keyword matching (BM25), producing better results than either method alone.

## Evaluation Framework

Mindspace includes a built-in evaluation system for measuring and improving retrieval quality. Philosophy: **you can't improve what you can't measure**.

```bash
# Interactively create eval cases from real queries
ms eval add-case

# Run evaluation against your golden dataset
ms eval run
ms eval run --k 10 --verbose

# Track improvement over time
ms eval history

# Compare last two runs (color-coded deltas)
ms eval compare

# View your golden dataset
ms eval golden
```

### Improving retrieval workflow

```bash
ms eval run                    # 1. Baseline
# ... make a change ...
ms admin reindex               # 2. Rebuild embeddings
ms eval run                    # 3. Measure
ms eval compare                # 4. See the impact
```

Metrics tracked: Precision@k, Recall@k, MRR (Mean Reciprocal Rank), Hit Rate, and Negative Leakage.

See [docs/eval-system.md](docs/eval-system.md) for full documentation.

## Administration

```bash
ms admin init      # Create data directories
ms admin stats     # Corpus statistics (counts by type/stream)
ms admin reindex   # Wipe derived data and re-embed everything
```

## Architecture

Event-sourced with strict layer separation. Each layer depends only downward:

```
cli/         → imports eval/, pipelines/, core/
eval/        → imports derived/, infra/, core/
pipelines/   → imports derived/, capture/, infra/, core/
derived/     → imports core/, infra/
infra/       → imports core/
capture/     → imports core/
core/        → imports nothing
```

```
src/mindspace/
├── core/          # Pure Pydantic models, ULID generation
├── capture/       # Raw JSON persistence, URL extraction (trafilatura)
├── infra/         # Adapters: OpenAI embeddings, ChromaDB, BM25 index
├── derived/       # Re-generable: embedding pipeline, chunking, text enrichment
├── eval/          # Evaluation: metrics, runner, history
├── pipelines/     # Orchestration: ingest, reindex
└── cli/           # Typer CLI: capture, search, admin, eval
```

### Key Design Decisions

- **Raw captures are permanent.** Immutable JSON events. You own them forever.
- **Intelligence is re-generable.** Embeddings, indexes, and derived data can be wiped and rebuilt from raw captures at any time (`ms admin reindex`).
- **Two streams.** External (what you encounter) and internal (what you think). The most interesting patterns emerge from the interplay.
- **Eval first, improve second.** Every retrieval change is measured before/after with the built-in eval framework.

### Retrieval Pipeline

1. **Text enrichment** — URL captures get title/tags prepended; reactions get parent context
2. **Chunking** — Long text split at paragraph/sentence boundaries (500 token chunks, 50 token overlap)
3. **Embedding** — Each chunk embedded via OpenAI `text-embedding-3-small`
4. **Vector storage** — Chunks stored in ChromaDB with metadata
5. **Keyword indexing** — Chunks indexed with BM25 for keyword matching
6. **Hybrid search** — Semantic + BM25 results fused via Reciprocal Rank Fusion (RRF)
7. **Deduplication** — Chunk results mapped back to capture IDs, best score kept

## Configuration

All settings via environment variables or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key (required) |
| `MINDSPACE_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `MINDSPACE_DATA_DIR` | `./data` | Data storage directory |
| `MINDSPACE_CHUNK_MAX_TOKENS` | `500` | Max words per chunk |
| `MINDSPACE_CHUNK_OVERLAP_TOKENS` | `50` | Word overlap between chunks |
| `MINDSPACE_HYBRID_SEARCH_ENABLED` | `True` | Enable BM25 + semantic fusion |

## Data Storage

All data lives under `data/` (gitignored):

```
data/
├── raw/                    # Immutable capture JSON files (one per capture)
├── index.jsonl             # Append-only capture index
├── derived/
│   ├── chroma/             # ChromaDB vector storage
│   ├── registry.json       # Tracks which captures have been embedded
│   └── bm25_corpus.json    # BM25 keyword index
└── eval/
    ├── golden.json          # Hand-curated evaluation dataset
    └── history.jsonl        # Eval run history
```

Raw captures are the source of truth. Everything under `derived/` can be deleted and rebuilt with `ms admin reindex`.

## Development

```bash
# Run tests (65 passing)
pytest

# Run specific test suites
pytest tests/eval/ -v           # Evaluation tests
pytest tests/derived/ -v        # Chunking + embedding tests
pytest tests/integration/ -v    # End-to-end tests

# Lint
ruff check src/ tests/
```

**Requirements:** Python 3.12+, OpenAI API key.

## Roadmap

- **Stage 1: Foundation + Capture + Retrieve** — Done
- **Stage 1.5: Retrieval Quality + Eval Framework** — Done
- **Stage 2: Intelligence** — Claude-powered summaries, concept extraction, connections, conversational query
- **Stage 3: Proactive** — Background processing, pattern detection, weekly digests
- **Stage 4: Deep Intelligence** — Gap detection, perspective diversity, temporal reasoning

See [ROADMAP.md](ROADMAP.md) for details.
