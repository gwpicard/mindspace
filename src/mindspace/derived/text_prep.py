"""Text enrichment for embedding quality."""

from mindspace.core.models import (
    Capture,
    CaptureType,
    ReactionContent,
    RepoContent,
    URLContent,
)


def _prepare_repo_text(content: dict) -> str:
    """Format repo content (raw or enriched) for embedding."""
    parts = []
    owner = content.get("owner", "")
    repo_name = content.get("repo_name", "")
    if owner and repo_name:
        parts.append(f"Title: {owner}/{repo_name}")
    if content.get("description"):
        parts.append(f"Description: {content['description']}")
    if content.get("language"):
        parts.append(f"Language: {content['language']}")
    if content.get("topics"):
        parts.append(f"Topics: {', '.join(content['topics'])}")
    if content.get("readme_text"):
        parts.append("")
        parts.append(content["readme_text"])
    return "\n".join(parts)


def prepare_text(capture: Capture, parent_capture: Capture | None = None) -> str:
    """Prepare enriched text for embedding.

    Checks for enriched content first (from reprocess pipeline).
    URL captures get title/tags prepended.
    Repo captures get structured metadata.
    Reactions get parent context prepended.
    Others use text_for_embedding() as-is.
    """
    from mindspace.pipelines.reprocess import load_enriched

    enriched = load_enriched(capture.id)
    if enriched:
        content = enriched.get("content", {})
        enriched_type = content.get("type")
        if enriched_type == "repo":
            return _prepare_repo_text(content)

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

    if capture.type == CaptureType.repo and isinstance(capture.content, RepoContent):
        return _prepare_repo_text(capture.content.model_dump())

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
