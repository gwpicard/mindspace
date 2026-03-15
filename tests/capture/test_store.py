"""Tests for capture store."""

from mindspace.capture import store
from mindspace.core.models import Capture, CaptureType, SnippetContent, Stream, ThoughtContent
from mindspace.infra.paths import ensure_dirs


def test_save_and_load(tmp_data_dir):
    ensure_dirs()
    content = SnippetContent(text="Test snippet")
    capture = Capture(stream=Stream.external, type=CaptureType.snippet, content=content)
    store.save(capture)

    loaded = store.load(capture.id)
    assert loaded.id == capture.id
    assert loaded.content.text == "Test snippet"
    assert loaded.type == CaptureType.snippet


def test_exists(tmp_data_dir):
    ensure_dirs()
    content = ThoughtContent(text="Test thought")
    capture = Capture(stream=Stream.internal, type=CaptureType.thought, content=content)

    assert not store.exists(capture.id)
    store.save(capture)
    assert store.exists(capture.id)


def test_iterate_all(tmp_data_dir):
    ensure_dirs()
    for i in range(3):
        c = Capture(
            stream=Stream.internal,
            type=CaptureType.thought,
            content=ThoughtContent(text=f"Thought {i}"),
        )
        store.save(c)

    all_captures = store.iterate_all()
    assert len(all_captures) == 3


def test_count_by_type(tmp_data_dir):
    ensure_dirs()
    store.save(Capture(stream=Stream.external, type=CaptureType.snippet, content=SnippetContent(text="a")))
    store.save(Capture(stream=Stream.external, type=CaptureType.snippet, content=SnippetContent(text="b")))
    store.save(Capture(stream=Stream.internal, type=CaptureType.thought, content=ThoughtContent(text="c")))

    by_type = store.count_by_type()
    assert by_type["snippet"] == 2
    assert by_type["thought"] == 1


def test_count_by_stream(tmp_data_dir):
    ensure_dirs()
    store.save(Capture(stream=Stream.external, type=CaptureType.snippet, content=SnippetContent(text="a")))
    store.save(Capture(stream=Stream.internal, type=CaptureType.thought, content=ThoughtContent(text="b")))

    by_stream = store.count_by_stream()
    assert by_stream["external"] == 1
    assert by_stream["internal"] == 1


def test_jsonl_index(tmp_data_dir):
    ensure_dirs()
    capture = Capture(stream=Stream.external, type=CaptureType.snippet, content=SnippetContent(text="test"))
    store.save(capture)

    from mindspace.infra.paths import index_path
    import json

    lines = index_path().read_text().strip().split("\n")
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["id"] == capture.id
    assert entry["type"] == "snippet"
