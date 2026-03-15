"""Tests for URL extraction (mocked HTTP)."""

from unittest.mock import patch, MagicMock

from mindspace.capture.extractors import extract_url


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
