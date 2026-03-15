"""Shared test fixtures."""

import os
import tempfile

import pytest

from mindspace.infra.config import reset_settings


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path, monkeypatch):
    """Use a temporary data directory for every test."""
    monkeypatch.setenv("MINDSPACE_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MINDSPACE_OPENAI_API_KEY", "test-key")
    reset_settings()
    yield tmp_path / "data"
    reset_settings()
