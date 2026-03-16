"""Ingest pipeline — orchestrates capture save + embedding derivation."""

from mindspace.capture import store
from mindspace.capture.extractors import extract_repo, extract_url
from mindspace.core.models import (
    CAPTURE_TYPE_TO_STREAM,
    Capture,
    CaptureContext,
    CaptureType,
    QuestionContent,
    ReactionContent,
    RepoContent,
    SnippetContent,
    ThoughtContent,
    URLContent,
)
from mindspace.derived.embeddings import EmbeddingPipeline


class DuplicateError(Exception):
    """Raised when a capture with the same URL already exists."""

    def __init__(self, existing: Capture):
        self.existing = existing
        super().__init__(f"Already captured as {existing.id}")


def ingest_url(
    url: str,
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a URL: fetch, extract, save, embed."""
    existing = store.find_by_url(url)
    if existing:
        raise DuplicateError(existing)
    extracted = extract_url(url)
    content = URLContent(**extracted)
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.url],
        type=CaptureType.url,
        content=content,
        context=CaptureContext(tags=tags or []),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture


def ingest_snippet(
    text: str,
    source_description: str | None = None,
    source_url: str | None = None,
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a text snippet."""
    content = SnippetContent(text=text, source_description=source_description, source_url=source_url)
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.snippet],
        type=CaptureType.snippet,
        content=content,
        context=CaptureContext(tags=tags or []),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture


def ingest_thought(
    text: str,
    thinking_type: str = "observation",
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a thought."""
    from mindspace.core.models import ThinkingType

    content = ThoughtContent(text=text, thinking_type=ThinkingType(thinking_type))
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.thought],
        type=CaptureType.thought,
        content=content,
        context=CaptureContext(tags=tags or []),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture


def ingest_question(
    text: str,
    urgency: str = "background",
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a question."""
    from mindspace.core.models import Urgency

    content = QuestionContent(text=text, urgency=Urgency(urgency))
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.question],
        type=CaptureType.question,
        content=content,
        context=CaptureContext(tags=tags or []),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture


def ingest_repo(
    url: str,
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a GitHub repo: fetch metadata + README, save, embed."""
    existing = store.find_by_url(url)
    if existing:
        raise DuplicateError(existing)
    extracted = extract_repo(url)
    content = RepoContent(**extracted)
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.repo],
        type=CaptureType.repo,
        content=content,
        context=CaptureContext(tags=tags or []),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture


def ingest_reaction(
    text: str,
    reacting_to: str,
    stance: str = "extend",
    tags: list[str] | None = None,
    pipeline: EmbeddingPipeline | None = None,
) -> Capture:
    """Capture a reaction to an existing capture."""
    from mindspace.core.models import Stance

    if not store.exists(reacting_to):
        raise ValueError(f"Capture {reacting_to} not found")

    content = ReactionContent(text=text, reacting_to=reacting_to, stance=Stance(stance))
    capture = Capture(
        stream=CAPTURE_TYPE_TO_STREAM[CaptureType.reaction],
        type=CaptureType.reaction,
        content=content,
        context=CaptureContext(tags=tags or [], related_ids=[reacting_to]),
    )
    store.save(capture)
    pipeline = pipeline or EmbeddingPipeline()
    pipeline.embed_capture(capture)
    return capture
