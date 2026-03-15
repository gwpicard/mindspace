"""Canonical Pydantic models — the contract everything depends on."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from mindspace.core.ids import generate_id


# --- Enums ---


class Stream(str, Enum):
    external = "external"
    internal = "internal"


class CaptureType(str, Enum):
    url = "url"
    snippet = "snippet"
    thought = "thought"
    reaction = "reaction"
    question = "question"


class ThinkingType(str, Enum):
    reflection = "reflection"
    hypothesis = "hypothesis"
    synthesis = "synthesis"
    observation = "observation"
    prediction = "prediction"


class Stance(str, Enum):
    agree = "agree"
    disagree = "disagree"
    extend = "extend"
    question = "question"
    synthesize = "synthesize"


class Urgency(str, Enum):
    active = "active"
    background = "background"
    someday = "someday"


# --- Content models ---


class URLContent(BaseModel):
    url: str
    title: str | None = None
    extracted_text: str | None = None
    excerpt: str | None = None
    author: str | None = None
    word_count: int | None = None
    language: str | None = None
    extraction_method: str | None = None
    raw_html_hash: str | None = None


class SnippetContent(BaseModel):
    text: str
    source_description: str | None = None
    source_url: str | None = None


class ThoughtContent(BaseModel):
    text: str
    thinking_type: ThinkingType = ThinkingType.observation


class ReactionContent(BaseModel):
    text: str
    reacting_to: str  # ULID of the capture being reacted to
    stance: Stance = Stance.extend


class QuestionContent(BaseModel):
    text: str
    domain: str | None = None
    urgency: Urgency = Urgency.background


ContentType = Annotated[
    Union[URLContent, SnippetContent, ThoughtContent, ReactionContent, QuestionContent],
    Field(discriminator=None),
]


# --- Context & Source ---


class CaptureContext(BaseModel):
    tags: list[str] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)
    project: str | None = None
    confidence: float | None = None


class CaptureSource(BaseModel):
    method: str = "cli"


# --- Capture ---


CAPTURE_TYPE_TO_CONTENT = {
    CaptureType.url: URLContent,
    CaptureType.snippet: SnippetContent,
    CaptureType.thought: ThoughtContent,
    CaptureType.reaction: ReactionContent,
    CaptureType.question: QuestionContent,
}

CAPTURE_TYPE_TO_STREAM = {
    CaptureType.url: Stream.external,
    CaptureType.snippet: Stream.external,
    CaptureType.thought: Stream.internal,
    CaptureType.reaction: Stream.internal,
    CaptureType.question: Stream.internal,
}


class Capture(BaseModel):
    id: str = Field(default_factory=generate_id)
    version: int = 1
    stream: Stream
    type: CaptureType
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: ContentType
    context: CaptureContext = Field(default_factory=CaptureContext)
    source: CaptureSource = Field(default_factory=CaptureSource)

    def text_for_embedding(self) -> str:
        """Extract the primary text content for embedding."""
        match self.content:
            case URLContent(title=title, extracted_text=text):
                parts = [p for p in [title, text] if p]
                return " ".join(parts)
            case SnippetContent(text=text):
                return text
            case ThoughtContent(text=text):
                return text
            case ReactionContent(text=text):
                return text
            case QuestionContent(text=text):
                return text
            case _:
                return ""
