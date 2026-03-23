"""Tests for resource processing — URL detection."""

import pytest

from mindspace.web.services.resource_processor import URL_RE


def test_url_detection():
    text = "Check out https://example.com/article and also http://github.com/foo/bar"
    urls = URL_RE.findall(text)
    assert len(urls) == 2
    assert "https://example.com/article" in urls
    assert "http://github.com/foo/bar" in urls


def test_url_detection_no_urls():
    text = "This is just a regular message with no links"
    urls = URL_RE.findall(text)
    assert len(urls) == 0


def test_url_detection_embedded():
    text = "I found this interesting: https://arxiv.org/abs/2301.01234 — what do you think?"
    urls = URL_RE.findall(text)
    assert len(urls) == 1
    assert "https://arxiv.org/abs/2301.01234" in urls
