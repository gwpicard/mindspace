"""Tests for core models."""

import json

from mindspace.core.models import (
    CAPTURE_TYPE_TO_STREAM,
    Capture,
    CaptureType,
    QuestionContent,
    SnippetContent,
    Stream,
    ThoughtContent,
    URLContent,
    Urgency,
)


def test_capture_url_serialization():
    content = URLContent(url="https://example.com", title="Example", extracted_text="Hello world")
    capture = Capture(
        stream=Stream.external,
        type=CaptureType.url,
        content=content,
    )
    data = capture.model_dump(mode="json")
    assert data["type"] == "url"
    assert data["stream"] == "external"
    assert data["content"]["url"] == "https://example.com"

    # Round-trip via JSON
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    assert parsed["id"] == capture.id


def test_capture_thought_serialization():
    content = ThoughtContent(text="This is a thought")
    capture = Capture(
        stream=Stream.internal,
        type=CaptureType.thought,
        content=content,
    )
    data = capture.model_dump(mode="json")
    assert data["type"] == "thought"
    assert data["content"]["thinking_type"] == "observation"


def test_text_for_embedding_url():
    content = URLContent(url="https://x.com", title="Title", extracted_text="Body text")
    capture = Capture(stream=Stream.external, type=CaptureType.url, content=content)
    assert capture.text_for_embedding() == "Title Body text"


def test_text_for_embedding_thought():
    content = ThoughtContent(text="My thought")
    capture = Capture(stream=Stream.internal, type=CaptureType.thought, content=content)
    assert capture.text_for_embedding() == "My thought"


def test_text_for_embedding_question():
    content = QuestionContent(text="Why?", urgency=Urgency.active)
    capture = Capture(stream=Stream.internal, type=CaptureType.question, content=content)
    assert capture.text_for_embedding() == "Why?"


def test_capture_type_to_stream_mapping():
    assert CAPTURE_TYPE_TO_STREAM[CaptureType.url] == Stream.external
    assert CAPTURE_TYPE_TO_STREAM[CaptureType.snippet] == Stream.external
    assert CAPTURE_TYPE_TO_STREAM[CaptureType.thought] == Stream.internal
    assert CAPTURE_TYPE_TO_STREAM[CaptureType.reaction] == Stream.internal
    assert CAPTURE_TYPE_TO_STREAM[CaptureType.question] == Stream.internal


def test_capture_has_ulid():
    content = SnippetContent(text="test")
    capture = Capture(stream=Stream.external, type=CaptureType.snippet, content=content)
    assert len(capture.id) == 26  # ULID string length
