# Mindspace — Roadmap

## Stage 1: Foundation + Capture + Retrieve [IN PROGRESS]

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

## Stage 2: Intelligence [PLANNED]

Claude-powered analysis layered on top of captures.

- Summary generation on ingest
- Concept/theme extraction
- Connection finding between captures
- Conversational query (`ms search ask "..."`)

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
