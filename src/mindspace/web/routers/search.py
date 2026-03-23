"""Search endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.web.deps import get_db

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    filters: dict | None = None  # channel_ids, types, date_range, cognitive_ops
    n_results: int = 10


class SearchResult(BaseModel):
    snippet: str
    distance: float
    source: str
    type: str
    metadata: dict = {}
    conversation_id: str | None = None
    conversation_title: str | None = None
    capture_id: str | None = None
    title: str | None = None


@router.post("")
async def search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> list[SearchResult]:
    from mindspace.web.services.search import SearchService

    svc = SearchService()

    channel_ids = None
    types = None
    if body.filters:
        channel_ids = body.filters.get("channel_ids")
        types = body.filters.get("types")

    results = await svc.search(
        query=body.query,
        db=db,
        n_results=body.n_results,
        channel_ids=channel_ids,
        types=types,
    )
    return [SearchResult(**r) for r in results]
