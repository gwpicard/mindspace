"""Tests for channel CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_channel(client: AsyncClient):
    resp = await client.post("/api/channels", json={"name": "Research", "description": "Research topics"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Research"
    assert data["description"] == "Research topics"


@pytest.mark.asyncio
async def test_list_channels(client: AsyncClient):
    await client.post("/api/channels", json={"name": "Alpha"})
    await client.post("/api/channels", json={"name": "Beta"})

    resp = await client.get("/api/channels")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_channel_detail(client: AsyncClient):
    create_resp = await client.post("/api/channels", json={"name": "Detail Channel"})
    chan_id = create_resp.json()["id"]

    resp = await client.get(f"/api/channels/{chan_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Detail Channel"
    assert "conversation_ids" in data


@pytest.mark.asyncio
async def test_update_channel(client: AsyncClient):
    create_resp = await client.post("/api/channels", json={"name": "Old Name"})
    chan_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/channels/{chan_id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_channel(client: AsyncClient):
    create_resp = await client.post("/api/channels", json={"name": "To Delete"})
    chan_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/channels/{chan_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/channels/{chan_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_assign_conversation_to_channel(client: AsyncClient):
    chan_resp = await client.post("/api/channels", json={"name": "Test Channel"})
    chan_id = chan_resp.json()["id"]

    conv_resp = await client.post("/api/conversations", json={"title": "Test Conv"})
    conv_id = conv_resp.json()["id"]

    # Assign conversation to channel
    resp = await client.patch(f"/api/conversations/{conv_id}", json={"channel_ids": [chan_id]})
    assert resp.status_code == 200
    assert chan_id in resp.json()["channel_ids"]

    # Verify channel shows the conversation
    chan_detail = await client.get(f"/api/channels/{chan_id}")
    assert conv_id in chan_detail.json()["conversation_ids"]
