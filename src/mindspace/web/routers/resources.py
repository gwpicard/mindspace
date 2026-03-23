"""Resource endpoints."""

from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.web.db.models import Resource
from mindspace.web.deps import get_db

router = APIRouter(prefix="/api/resources", tags=["resources"])


class ResourceOut(BaseModel):
    id: str
    type: str
    source_url: str | None
    title: str | None
    processing_status: str
    processing_error: str | None
    created_at: datetime
    conversation_id: str | None
    metadata: dict | None = None

    model_config = {"from_attributes": True}


class ResourceDetailOut(ResourceOut):
    raw_content: str | None = None


@router.get("")
async def list_resources(
    status: str | None = Query(None),
    type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[ResourceOut]:
    query = select(Resource).order_by(Resource.created_at.desc()).limit(limit)
    if status:
        query = query.where(Resource.processing_status == status)
    if type:
        query = query.where(Resource.type == type)
    result = await db.execute(query)
    return [_resource_out(r) for r in result.scalars().all()]


@router.get("/{resource_id}")
async def get_resource(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResourceDetailOut:
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    out = _resource_out(resource)
    return ResourceDetailOut(**out.model_dump(), raw_content=resource.raw_content)


def _resource_out(r: Resource) -> ResourceOut:
    metadata = None
    if r.metadata_json:
        try:
            metadata = json.loads(r.metadata_json)
        except (json.JSONDecodeError, TypeError):
            metadata = None
    return ResourceOut(
        id=r.id,
        type=r.type,
        source_url=r.source_url,
        title=r.title,
        processing_status=r.processing_status,
        processing_error=r.processing_error,
        created_at=r.created_at,
        conversation_id=r.conversation_id,
        metadata=metadata,
    )
