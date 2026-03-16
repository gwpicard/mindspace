"""Tests for capture store."""

from mindspace.capture import store
from mindspace.core.models import Capture, CaptureType, SnippetContent, Stream, ThoughtContent, URLContent, RepoContent
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


def test_find_by_url(tmp_data_dir):
    ensure_dirs()
    content = URLContent(url="https://example.com/page", title="Test")
    capture = Capture(stream=Stream.external, type=CaptureType.url, content=content)
    store.save(capture)

    found = store.find_by_url("https://example.com/page")
    assert found is not None
    assert found.id == capture.id

    assert store.find_by_url("https://example.com/other") is None


def test_find_by_url_repo(tmp_data_dir):
    ensure_dirs()
    content = RepoContent(url="https://github.com/owner/repo", owner="owner", repo_name="repo")
    capture = Capture(stream=Stream.external, type=CaptureType.repo, content=content)
    store.save(capture)

    found = store.find_by_url("https://github.com/owner/repo")
    assert found is not None
    assert found.id == capture.id


def test_rebuild_index(tmp_data_dir):
    ensure_dirs()
    store.save(Capture(stream=Stream.external, type=CaptureType.snippet, content=SnippetContent(text="a")))
    store.save(Capture(stream=Stream.internal, type=CaptureType.thought, content=ThoughtContent(text="b")))

    # Corrupt the index
    from mindspace.infra.paths import index_path
    index_path().write_text("garbage\n")

    count = store.rebuild_index()
    assert count == 2

    import json
    lines = index_path().read_text().strip().split("\n")
    assert len(lines) == 2
    for line in lines:
        entry = json.loads(line)
        assert "id" in entry
        assert "type" in entry
