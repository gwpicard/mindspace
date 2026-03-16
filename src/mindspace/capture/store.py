"""Raw capture persistence — JSON files + JSONL index."""

import json
from pathlib import Path

from mindspace.core.models import PROCESS_VERSION, Capture
from mindspace.infra.paths import index_path, raw_dir


def _capture_path(capture_id: str) -> Path:
    """Path for a single capture's JSON file."""
    return raw_dir() / f"{capture_id}.json"


def save(capture: Capture) -> Path:
    """Save a capture as a JSON file and append to the JSONL index."""
    path = _capture_path(capture.id)
    data = capture.model_dump(mode="json")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    _append_index(capture)
    return path


def load(capture_id: str) -> Capture:
    """Load a capture by ID."""
    path = _capture_path(capture_id)
    data = json.loads(path.read_text())
    return _deserialize(data)


def exists(capture_id: str) -> bool:
    """Check if a capture exists."""
    return _capture_path(capture_id).exists()


def iterate_all() -> list[Capture]:
    """Load all captures from the raw directory."""
    captures = []
    for path in sorted(raw_dir().glob("*.json")):
        data = json.loads(path.read_text())
        captures.append(_deserialize(data))
    return captures


def count() -> int:
    """Count total captures."""
    return len(list(raw_dir().glob("*.json")))


def count_by_type() -> dict[str, int]:
    """Count captures grouped by type."""
    counts: dict[str, int] = {}
    for path in raw_dir().glob("*.json"):
        data = json.loads(path.read_text())
        ctype = data.get("type", "unknown")
        counts[ctype] = counts.get(ctype, 0) + 1
    return counts


def count_by_stream() -> dict[str, int]:
    """Count captures grouped by stream."""
    counts: dict[str, int] = {}
    for path in raw_dir().glob("*.json"):
        data = json.loads(path.read_text())
        stream = data.get("stream", "unknown")
        counts[stream] = counts.get(stream, 0) + 1
    return counts


def all_tags() -> list[tuple[str, int]]:
    """Return all tags sorted by frequency (descending)."""
    counts: dict[str, int] = {}
    idx = index_path()
    if idx.exists():
        for line in idx.read_text().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            for tag in entry.get("tags", []):
                counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def _append_index(capture: Capture) -> None:
    """Append a capture summary to the JSONL index."""
    entry = {
        "id": capture.id,
        "type": capture.type.value,
        "stream": capture.stream.value,
        "created_at": capture.created_at.isoformat(),
        "tags": capture.context.tags,
        "process_version": PROCESS_VERSION,
    }
    with open(index_path(), "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _deserialize(data: dict) -> Capture:
    """Deserialize a capture dict, mapping content to the correct type."""
    from mindspace.core.models import CAPTURE_TYPE_TO_CONTENT, CaptureType

    ctype = CaptureType(data["type"])
    content_cls = CAPTURE_TYPE_TO_CONTENT[ctype]
    data["content"] = content_cls(**data["content"])
    return Capture(**data)
