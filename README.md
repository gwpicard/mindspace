# Mindspace

A personal intelligence system that ingests what you encounter (articles, URLs) and what you think (reactions, thoughts, questions), embeds everything for semantic retrieval, and progressively layers intelligence on top — surfacing patterns, connections, and gaps in your thinking.

**Core insight:** You already have good signal detection. The bottleneck isn't finding interesting things — it's processing and connecting them over time. Mindspace closes that loop.

## What Mindspace Is Not

- Not a note-taking app (no manual organization required)
- Not a bookmarking tool (captures are processed, not just saved)
- Not a chatbot (intelligence is grounded in your actual corpus)
- Not a search engine (it knows what you've already seen and thought)

## Quick Start

### Web App (recommended)

```bash
# Clone
git clone https://github.com/gwpicard/mindspace.git
cd mindspace

# Configure
cp .env.example .env
# Edit .env and add your API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)

# Install dependencies
uv sync
cd frontend && npm install && cd ..

# Run both servers
./run/dev.sh
```

Open http://localhost:5173. The web app provides conversations with Claude (organized into channels), semantic search across your corpus, and a resource library.

### Production (single process)

```bash
cd frontend && npm run build && cd ..
uv run uvicorn mindspace.web.app:create_app --factory --port 8000
```

The backend serves the built SPA — no separate frontend server needed. Open http://localhost:8000.

### Devcontainer

Open the project in VS Code or any devcontainer-compatible editor. The `.devcontainer/` config sets up Python 3.12, Node 22, uv, and Playwright automatically.

### CLI

The original CLI is still available for direct capture and search:

```bash
# Capture
ms capture url "https://example.com/interesting-article" --tag ai --tag research
ms capture thought --text "LLMs are changing how we approach software architecture"

# Search
ms search query "artificial intelligence"
```

## Web App

The web interface is a SvelteKit SPA backed by a FastAPI API server.

**Conversations** — Chat with Claude, grounded in your personal corpus. Conversations are organized into channels (topics/themes). Claude automatically detects and captures URLs you share.

**Channels** — Group conversations by topic. Add/remove channels per conversation, edit channel names, or delete channels from the channel detail page.

**Search** — Cmd+K opens semantic search across all conversations and resources. Hybrid retrieval (embeddings + BM25) via Reciprocal Rank Fusion.

**Library** — Browse all captured resources (articles, repos, snippets, notes).

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

## Evaluation Framework

Built-in evaluation system for measuring and improving retrieval quality. Philosophy: **you can't improve what you can't measure**.

```bash
ms eval add-case              # Interactively create eval cases
ms eval run                   # Run evaluation
ms eval run --k 10 --verbose  # With options
ms eval history               # Track improvement over time
ms eval compare               # Compare last two runs
ms eval golden                # View golden dataset
```

Metrics tracked: Precision@k, Recall@k, MRR (Mean Reciprocal Rank), Hit Rate, and Negative Leakage.

See [docs/eval-system.md](docs/eval-system.md) for full documentation.

## Architecture

```
src/mindspace/
├── core/          # Pure Pydantic models, ULID generation
├── capture/       # Raw JSON persistence, URL extraction (trafilatura)
├── infra/         # Adapters: OpenAI embeddings, ChromaDB, BM25 index
├── derived/       # Re-generable: embedding pipeline, chunking, text enrichment
├── eval/          # Evaluation: metrics, runner, history
├── pipelines/     # Orchestration: ingest, reindex
├── cli/           # Typer CLI: capture, search, admin, eval
└── web/           # FastAPI backend: conversations, channels, resources, search
    ├── routers/   # API endpoints
    ├── services/  # Chat (Claude SSE), resource processing
    └── db/        # SQLAlchemy async models + engine (SQLite)

frontend/          # SvelteKit SPA
├── src/
│   ├── lib/       # API client, stores (Svelte), components
│   └── routes/    # Pages: home, conversation, channel, resource
└── e2e/           # Playwright E2E tests
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
| `ANTHROPIC_API_KEY` | — | Anthropic API key (for Claude chat) |
| `OPENAI_API_KEY` | — | OpenAI API key (for embeddings) |
| `MINDSPACE_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `MINDSPACE_DATA_DIR` | `./data` | Data storage directory |
| `MINDSPACE_CHUNK_MAX_TOKENS` | `500` | Max words per chunk |
| `MINDSPACE_CHUNK_OVERLAP_TOKENS` | `50` | Word overlap between chunks |
| `MINDSPACE_HYBRID_SEARCH_ENABLED` | `True` | Enable BM25 + semantic fusion |

## Development

```bash
# Run both servers (backend + frontend)
./run/dev.sh

# Backend tests
pytest
pytest tests/eval/ -v           # Evaluation tests
pytest tests/derived/ -v        # Chunking + embedding tests
pytest tests/integration/ -v    # End-to-end tests

# Frontend E2E tests (starts servers automatically)
cd frontend && npm run test:e2e

# Lint
ruff check src/ tests/
```

**Requirements:** Python 3.12+, Node.js 22+, OpenAI API key, Anthropic API key.

## Roadmap

- **Stage 1: Foundation + Capture + Retrieve** — Done
- **Stage 1.5: Retrieval Quality + Eval Framework** — Done
- **Stage 2: Intelligence** — Claude-powered summaries, concept extraction, connections, conversational query
- **Stage 3: Proactive** — Background processing, pattern detection, weekly digests
- **Stage 4: Deep Intelligence** — Gap detection, perspective diversity, temporal reasoning

See [ROADMAP.md](ROADMAP.md) for details.
