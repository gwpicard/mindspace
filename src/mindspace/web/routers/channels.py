"""Channel CRUD endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mindspace.core.ids import generate_id
from mindspace.web.db.models import Channel
from mindspace.web.deps import get_db

router = APIRouter(prefix="/api/channels", tags=["channels"])


# --- Schemas ---


class ChannelCreate(BaseModel):
    name: str
    description: str | None = None


class ChannelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ChannelOut(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChannelDetail(ChannelOut):
    conversation_ids: list[str] = []


# --- Routes ---


@router.post("", status_code=201)
async def create_channel(
    body: ChannelCreate,
    db: AsyncSession = Depends(get_db),
) -> ChannelOut:
    channel = Channel(id=generate_id(), name=body.name, description=body.description)
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return ChannelOut.model_validate(channel)


@router.get("")
async def list_channels(
    db: AsyncSession = Depends(get_db),
) -> list[ChannelOut]:
    result = await db.execute(select(Channel).order_by(Channel.name))
    return [ChannelOut.model_validate(c) for c in result.scalars().all()]


@router.get("/{channel_id}")
async def get_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
) -> ChannelDetail:
    result = await db.execute(
        select(Channel)
        .where(Channel.id == channel_id)
        .options(selectinload(Channel.conversations))
    )
    channel = result.scalar_one_or_none()
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelDetail(
        id=channel.id,
        name=channel.name,
        description=channel.description,
        created_at=channel.created_at,
        conversation_ids=[c.id for c in channel.conversations],
    )


@router.patch("/{channel_id}")
async def update_channel(
    channel_id: str,
    body: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
) -> ChannelOut:
    channel = await db.get(Channel, channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if body.name is not None:
        channel.name = body.name
    if body.description is not None:
        channel.description = body.description
    await db.commit()
    await db.refresh(channel)
    return ChannelOut.model_validate(channel)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    channel = await db.get(Channel, channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db.delete(channel)
    await db.commit()
