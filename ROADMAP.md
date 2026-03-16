# Mindspace — Roadmap

## Stage 1: Foundation + Capture + Retrieve [DONE]

Core capture loop: ingest external and internal captures, embed them, search semantically.

- [x] Project scaffolding (pyproject.toml, .gitignore, .env.example)
- [x] Core models (Pydantic capture models, ULID IDs)
- [x] Config + paths (pydantic-settings, data directory resolution)
- [x] Capture store (JSON persistence + JSONL index)
- [x] URL extraction (trafilatura)
- [x] Embedding adapter (OpenAI text-embedding-3-small)
- [x] Vector DB adapter (ChromaDB)
- [x] Embedding pipeline (embed + store)
- [x] Ingest + reindex pipelines
- [x] CLI commands (capture, search, admin)
- [x] Tests (unit + integration, 27 passing)

## Stage 1.5: Retrieval Quality + Evaluation Framework [DONE]

Eval-first approach to improving retrieval quality. Measure before/after every change.

- [x] Eval types + pure metric functions (precision@k, recall@k, MRR, hit rate)
- [x] Eval runner + JSONL history persistence
- [x] Eval CLI (run, history, compare, add-case, golden)
- [x] Text chunking for long captures (paragraph-aware, configurable overlap)
- [x] Hybrid search (BM25 + semantic via Reciprocal Rank Fusion)
- [x] Text enrichment for embeddings (URL title/tags, reaction context)
- [x] Retrieval regression tests with golden dataset fixture
- [x] Tests (65 passing)

## Stage 2: Intelligence [PLANNED]

Claude-powered analysis layered on top of captures.

- Summary generation on ingest
- Concept/theme extraction
- Connection finding between captures
- Conversational query (`ms search ask "..."`)
- RAG Triad evals (groundedness, answer relevance via Claude judge)
- HyDE query enhancement (optional search mode)
- Claude-based re-ranking

## Stage 3: Proactive [PLANNED]

Background intelligence that works without being asked.

- Background processing daemon
- Pattern detection over time
- Two-stream analysis (external vs internal interplay)
- Weekly digest generation

## Stage 4: Deep Intelligence [PLANNED]

Sophisticated gap detection and meta-cognition.

- Gap detection (external anchoring, question failure, concept co-occurrence)
- Perspective diversity analysis
- Temporal reasoning
- Blind spot challenging
