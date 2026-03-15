"""URL content extraction using trafilatura."""

from __future__ import annotations

import hashlib

import httpx
import trafilatura


def extract_url(url: str) -> dict:
    """Fetch a URL and extract its main text content.

    Returns a dict with fields matching URLContent.
    """
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    html = response.text

    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        output_format="txt",
    )

    metadata = trafilatura.extract(
        html,
        include_comments=False,
        output_format="xmltei",
    )

    title = None
    author = None
    if metadata:
        # Try to parse title and author from TEI XML
        import re

        title_match = re.search(r"<title[^>]*>([^<]+)</title>", metadata)
        if title_match:
            title = title_match.group(1).strip()
        author_match = re.search(r"<author>([^<]+)</author>", metadata)
        if author_match:
            author = author_match.group(1).strip()

    text = extracted or ""
    word_count = len(text.split()) if text else 0

    return {
        "url": url,
        "title": title,
        "extracted_text": text if text else None,
        "excerpt": text[:500] if text else None,
        "author": author,
        "word_count": word_count,
        "language": None,
        "extraction_method": "trafilatura",
        "raw_html_hash": hashlib.sha256(html.encode()).hexdigest()[:16],
    }
