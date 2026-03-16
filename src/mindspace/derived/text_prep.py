"""Text enrichment for embedding quality."""

from mindspace.core.models import (
    Capture,
    CaptureType,
    ReactionContent,
    URLContent,
)


def prepare_text(capture: Capture, parent_capture: Capture | None = None) -> str:
    """Prepare enriched text for embedding.

    URL captures get title/tags prepended.
    Reactions get parent context prepended.
    Others use text_for_embedding() as-is.
    """
    if capture.type == CaptureType.url and isinstance(capture.content, URLContent):
        parts = []
        if capture.content.title:
            parts.append(f"Title: {capture.content.title}")
        if capture.context.tags:
            parts.append(f"Tags: {', '.join(capture.context.tags)}")
        text = capture.content.extracted_text or ""
        if parts:
            return "\n".join(parts) + "\n\n" + text
        return text

    if capture.type == CaptureType.reaction and isinstance(capture.content, ReactionContent):
        parts = []
        if parent_capture:
            parent_text = parent_capture.text_for_embedding()[:200]
            parts.append(f"Reacting to: {parent_text}")
        parts.append(f"Stance: {capture.content.stance.value}")
        parts.append("")
        parts.append(capture.content.text)
        return "\n".join(parts)

    return capture.text_for_embedding()
