"""Tests for conversation CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient):
    resp = await client.post("/api/conversations", json={"title": "Test Conv"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Conv"
    assert data["id"]


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient):
    await client.post("/api/conversations", json={"title": "Conv 1"})
    await client.post("/api/conversations", json={"title": "Conv 2"})

    resp = await client.get("/api/conversations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations", json={"title": "Detail Test"})
    conv_id = create_resp.json()["id"]

    resp = await client.get(f"/api/conversations/{conv_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Detail Test"
    assert "messages" in data


@pytest.mark.asyncio
async def test_update_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations", json={"title": "Old Title"})
    conv_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/conversations/{conv_id}", json={"title": "New Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations", json={"title": "To Delete"})
    conv_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/conversations/{conv_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/conversations/{conv_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_conversation(client: AsyncClient):
    resp = await client.get("/api/conversations/nonexistent")
    assert resp.status_code == 404
