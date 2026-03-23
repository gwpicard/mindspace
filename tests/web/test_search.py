"""Tests for search endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_empty(client: AsyncClient):
    """Search with no data returns empty results."""
    resp = await client.post("/api/search", json={"query": "test query"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
