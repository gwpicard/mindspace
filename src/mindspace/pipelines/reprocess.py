"""Reprocess pipeline — re-extract content and rebuild enriched layer."""

import json
from datetime import datetime, timezone

from mindspace.capture import store
from mindspace.capture.extractors import extract_repo, parse_github_url
from mindspace.core.models import PROCESS_VERSION, Capture, CaptureType
from mindspace.infra.paths import enriched_dir
from mindspace.pipelines.reindex import reindex


def _enriched_path(capture_id: str):
    return enriched_dir() / f"{capture_id}.json"


def load_enriched(capture_id: str) -> dict | None:
    """Load enriched content for a capture, or None if not found."""
    path = _enriched_path(capture_id)
    if path.exists():
        return json.loads(path.read_text())
    return None


def save_enriched(capture_id: str, content: dict) -> None:
    """Save enriched content for a capture."""
    enriched_dir().mkdir(parents=True, exist_ok=True)
    data = {
        "capture_id": capture_id,
        "process_version": PROCESS_VERSION,
        "content": content,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    _enriched_path(capture_id).write_text(
        json.dumps(data, indent=2, ensure_ascii=False)
    )


def _reprocess_capture(capture: Capture) -> bool:
    """Re-extract content for a single capture. Returns True if enriched."""
    existing = load_enriched(capture.id)
    if existing and existing.get("process_version") == PROCESS_VERSION:
        return False

    # Smart URL → repo upgrade
    if capture.type == CaptureType.url:
        url = capture.content.url
        parsed = parse_github_url(url)
        if parsed:
            try:
                repo_data = extract_repo(url)
                save_enriched(capture.id, {"type": "repo", **repo_data})
                return True
            except Exception:
                pass

    return False


def reprocess(
    reindex_after: bool = True,
    **reindex_kwargs,
) -> dict:
    """Re-extract content for all captures, then optionally reindex.

    Returns stats dict.
    """
    captures = store.iterate_all()
    enriched = 0
    skipped = 0

    for capture in captures:
        if _reprocess_capture(capture):
            enriched += 1
        else:
            skipped += 1

    stats = {
        "total": len(captures),
        "enriched": enriched,
        "skipped": skipped,
    }

    if reindex_after:
        reindex_stats = reindex(**reindex_kwargs)
        stats["reindex"] = reindex_stats

    return stats
