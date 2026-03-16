"""Tag autosuggestion based on existing tags and content keywords."""

from __future__ import annotations

import re
from collections import Counter

STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "ought",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
    "they", "them", "their", "this", "that", "these", "those", "what",
    "which", "who", "whom", "how", "when", "where", "why",
    "and", "or", "but", "if", "then", "so", "as", "of", "in", "on",
    "at", "to", "for", "with", "by", "from", "about", "into", "through",
    "not", "no", "nor", "very", "just", "also", "than", "more", "most",
    "some", "any", "all", "each", "every", "both", "few", "many", "much",
    "other", "another", "such", "only", "own", "same", "new", "old",
    "one", "two", "three", "first", "last", "long", "great", "little",
    "right", "big", "high", "different", "small", "large", "next", "early",
    "important", "still", "even", "after", "before", "between", "under",
    "over", "up", "down", "out", "off", "here", "there", "again",
    "http", "https", "www", "com", "org", "net",
})

_WORD_RE = re.compile(r"[a-z][a-z0-9-]+")


def _tokenize(text: str) -> list[str]:
    """Extract lowercase tokens from text, filtering stopwords and short words."""
    words = _WORD_RE.findall(text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) >= 3]


def suggest_tags(
    text: str,
    existing_tags: list[tuple[str, int]],
    source_tags: list[str] | None = None,
    max_suggestions: int = 4,
) -> list[str]:
    """Suggest tags for a capture based on content and existing corpus tags.

    Args:
        text: The capture text content.
        existing_tags: (tag, count) pairs from the corpus, sorted by frequency.
        source_tags: Extra tags from the source (e.g. GitHub topics, language).
        max_suggestions: Maximum number of suggestions to return.

    Returns:
        List of suggested tag strings, up to max_suggestions.
    """
    suggestions: list[str] = []
    tokens = set(_tokenize(text))

    # 1. Existing tags that overlap with content words (prefer frequent ones)
    for tag, _count in existing_tags:
        if len(suggestions) >= max_suggestions:
            break
        tag_words = set(_WORD_RE.findall(tag.lower()))
        if tag_words & tokens and tag not in suggestions:
            suggestions.append(tag)

    # 2. Source-specific tags (e.g. GitHub topics, language)
    if source_tags:
        for tag in source_tags:
            if len(suggestions) >= max_suggestions:
                break
            normalized = tag.lower().strip()
            if normalized and normalized not in suggestions:
                suggestions.append(normalized)

    # 3. Content-derived keywords to fill remaining slots
    if len(suggestions) < max_suggestions:
        word_counts = Counter(_tokenize(text))
        existing_tag_set = {t for t, _ in existing_tags}
        for word, _count in word_counts.most_common():
            if len(suggestions) >= max_suggestions:
                break
            if word not in suggestions and word not in existing_tag_set:
                suggestions.append(word)

    return suggestions[:max_suggestions]
