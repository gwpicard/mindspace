"""Tests for URL and repo extraction (mocked HTTP)."""

from unittest.mock import patch, MagicMock

from mindspace.capture.extractors import extract_repo, extract_url, parse_github_url


SAMPLE_HTML = """
<html>
<head><title>Test Article</title></head>
<body>
<article>
<h1>Test Article</h1>
<p>This is a test article with enough content to extract.</p>
<p>It has multiple paragraphs to ensure trafilatura finds text.</p>
</article>
</body>
</html>
"""


def test_extract_url_basic():
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()

    with (
        patch("mindspace.capture.extractors.httpx.get", return_value=mock_response),
        patch("mindspace.capture.extractors.trafilatura.extract", return_value="Extracted text content"),
    ):
        result = extract_url("https://example.com/article")

    assert result["url"] == "https://example.com/article"
    assert result["extracted_text"] == "Extracted text content"
    assert result["extraction_method"] == "trafilatura"
    assert result["raw_html_hash"] is not None
    assert result["word_count"] == 3


def test_extract_url_no_content():
    mock_response = MagicMock()
    mock_response.text = "<html><body></body></html>"
    mock_response.raise_for_status = MagicMock()

    with (
        patch("mindspace.capture.extractors.httpx.get", return_value=mock_response),
        patch("mindspace.capture.extractors.trafilatura.extract", return_value=None),
    ):
        result = extract_url("https://example.com/empty")

    assert result["url"] == "https://example.com/empty"
    assert result["extracted_text"] is None
    assert result["word_count"] == 0


def test_parse_github_url():
    assert parse_github_url("https://github.com/anthropics/claude-code") == ("anthropics", "claude-code")
    assert parse_github_url("https://github.com/owner/repo.git") == ("owner", "repo")
    assert parse_github_url("https://github.com/owner/repo/") == ("owner", "repo")
    assert parse_github_url("https://example.com/not-github") is None


def test_extract_repo():
    meta_response = MagicMock()
    meta_response.status_code = 200
    meta_response.json.return_value = {
        "description": "A cool tool",
        "stargazers_count": 1234,
        "language": "Python",
        "topics": ["cli", "ai"],
        "updated_at": "2026-03-15T00:00:00Z",
    }
    meta_response.raise_for_status = MagicMock()

    readme_response = MagicMock()
    readme_response.status_code = 200
    readme_response.text = "# README\nThis is the readme."

    def mock_get(url, **kwargs):
        if "/readme" in url:
            return readme_response
        return meta_response

    with patch("mindspace.capture.extractors.httpx.get", side_effect=mock_get):
        result = extract_repo("https://github.com/anthropics/claude-code")

    assert result["owner"] == "anthropics"
    assert result["repo_name"] == "claude-code"
    assert result["description"] == "A cool tool"
    assert result["stars"] == 1234
    assert result["language"] == "Python"
    assert result["topics"] == ["cli", "ai"]
    assert result["readme_text"] == "# README\nThis is the readme."
