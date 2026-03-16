# Mindspace — Personal Intelligence System

## Vision

Mindspace is a personal intelligence system that ingests what you encounter (articles, URLs) and what you think (reactions, thoughts, questions), embeds everything for semantic retrieval, and progressively layers intelligence on top — surfacing patterns, connections, and gaps in your thinking.

**Core insight:** You already have good signal detection. The bottleneck isn't finding interesting things — it's processing and connecting them over time. Mindspace closes that loop.

## Principles

1. **Raw captures are permanent.** Every capture is an immutable JSON event in an open format. You own it forever. Everything else is disposable.
2. **Intelligence is re-generable.** Embeddings, summaries, connections, clusters — all derived from raw captures. Delete them, rebuild anytime.
3. **Two streams.** External (what you encounter) and internal (what you think). The most interesting intelligence emerges from the interplay between them.
4. **Emergent taxonomy.** Categories and themes emerge from the data, not from upfront design. Faceted: domain, theme, temporal relevance, confidence, novelty-to-corpus, perspective.
5. **Longitudinal self-portrait.** Over time, Mindspace reflects how you think — your intellectual fingerprint, blind spots, recurring questions, and evolving interests.

## What Mindspace Is Not

- Not a note-taking app (no manual organization required)
- Not a bookmarking tool (captures are processed, not just saved)
- Not a chatbot (intelligence is grounded in your actual corpus)
- Not a search engine (it knows what you've already seen and thought)

## Architecture

Event-sourced, strict layer separation. Each layer depends only downward:

- **Core** — Pure Pydantic models, zero dependencies
- **Capture** — Raw read/write, imports only Core
- **Infrastructure** — Swappable adapters (embeddings, vector DB)
- **Derived** — Re-generable from raw (embeddings, registry)
- **Intelligence** — Analysis, connections, patterns (future)
- **Pipelines** — Orchestration wiring
- **CLI** — Presentation layer, replaceable

## Evaluation Philosophy

**You can't improve what you can't measure.** (Inspired by Hamel Husain)

Retrieval quality is evaluated through a domain-specific, hand-curated golden dataset — not generic frameworks like RAGAS or TruLens. The eval framework follows these principles:

- **Eval first, improve second** — every retrieval change is measured before/after
- **Binary pass/fail** — a case passes if expected captures appear in top-k results
- **Simple tooling** — JSON files, pytest, CLI commands. No frameworks.
- **Domain-specific** — golden dataset is curated from your actual captures and queries
- **Extensible** — Stage 2 adds RAG Triad metrics (Groundedness, Answer Relevance) when generation is introduced

Metrics tracked: Precision@k, Recall@k, MRR (Mean Reciprocal Rank), Hit Rate, Negative Leakage.

## Modes (Future)

- **Passive:** Background processing on ingest
- **Proactive:** Surface patterns, generate digests
- **Active:** Conversational query grounded in your corpus
