"""Content extraction for URLs and GitHub repos."""

from __future__ import annotations

import hashlib
import re

import httpx
import trafilatura

_GITHUB_REPO_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?/?$"
)


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


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Parse owner/repo from a GitHub URL. Returns (owner, repo) or None."""
    m = _GITHUB_REPO_RE.search(url)
    if m:
        return m.group("owner"), m.group("repo")
    return None


def extract_repo(url: str) -> dict:
    """Fetch GitHub repo metadata and README via the public API.

    Returns a dict with fields matching RepoContent.
    """
    parsed = parse_github_url(url)
    if not parsed:
        raise ValueError(f"Not a valid GitHub repo URL: {url}")

    owner, repo_name = parsed
    api_base = f"https://api.github.com/repos/{owner}/{repo_name}"

    # Fetch repo metadata
    resp = httpx.get(api_base, timeout=30)
    resp.raise_for_status()
    meta = resp.json()

    # Fetch README
    readme_text = None
    try:
        readme_resp = httpx.get(
            f"{api_base}/readme",
            headers={"Accept": "application/vnd.github.raw"},
            timeout=30,
        )
        if readme_resp.status_code == 200:
            readme_text = readme_resp.text
    except httpx.HTTPError:
        pass

    return {
        "url": url,
        "owner": owner,
        "repo_name": repo_name,
        "description": meta.get("description"),
        "stars": meta.get("stargazers_count"),
        "language": meta.get("language"),
        "topics": meta.get("topics", []),
        "readme_text": readme_text,
        "last_updated": meta.get("updated_at"),
    }
