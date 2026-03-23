"""Resource processing — detect URLs, extract content, embed."""

from __future__ import annotations

import asyncio
import json
import logging
import re

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.core.ids import generate_id
from mindspace.web.db.models import Resource
from mindspace.web import tasks as task_manager

logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


@dataclass
class DuplicateResource:
    """A URL that was already captured previously."""
    id: str
    url: str
    title: str | None
    conversation_id: str | None


@dataclass
class ProcessingResult:
    """Result of URL detection: new resources and duplicates."""
    resources: list[Resource]
    duplicates: list[DuplicateResource]


async def detect_and_process_urls(
    text: str,
    message_id: str,
    conversation_id: str,
    db: AsyncSession,
) -> ProcessingResult:
    """Detect URLs in text, create Resource records, and trigger background processing."""
    urls = URL_RE.findall(text)
    if not urls:
        return ProcessingResult(resources=[], duplicates=[])

    resources = []
    duplicates = []
    for url in set(urls):  # deduplicate within message
        # Check if URL was already captured
        existing = await db.execute(
            select(Resource).where(Resource.source_url == url).limit(1)
        )
        existing_resource = existing.scalar_one_or_none()
        if existing_resource:
            duplicates.append(DuplicateResource(
                id=existing_resource.id,
                url=url,
                title=existing_resource.title,
                conversation_id=existing_resource.conversation_id,
            ))
            continue

        from mindspace.capture.extractors import parse_github_url

        resource_type = "repo" if parse_github_url(url) else "url"

        resource = Resource(
            id=generate_id(),
            type=resource_type,
            source_url=url,
            processing_status="pending",
            message_id=message_id,
            conversation_id=conversation_id,
        )
        db.add(resource)
        resources.append(resource)

    await db.commit()

    # Trigger background processing for each new resource
    for resource in resources:
        task_manager.submit(
            _process_resource(resource.id),
            name=f"resource-{resource.id}",
        )

    return ProcessingResult(resources=resources, duplicates=duplicates)


async def _process_resource(resource_id: str) -> None:
    """Background task: extract content, chunk, embed."""
    from mindspace.web.db.engine import get_session_factory

    async with get_session_factory()() as db:
        resource = await db.get(Resource, resource_id)
        if resource is None:
            return

        resource.processing_status = "processing"
        await db.commit()

        try:
            extracted = await _extract_content(resource)
            resource.title = extracted.get("title")
            resource.raw_content = extracted.get("text", "")
            resource.metadata_json = json.dumps(extracted.get("metadata", {}))
            resource.processing_status = "completed"
            await db.commit()

            # Embed the content
            await _embed_resource(resource)

            resource.is_embedded = True
            await db.commit()
            logger.info("Resource %s processed: %s", resource_id, resource.title)

        except Exception as e:
            resource.processing_status = "failed"
            resource.processing_error = str(e)
            await db.commit()
            logger.error("Resource %s failed: %s", resource_id, e)


async def _extract_content(resource: Resource) -> dict:
    """Extract content using existing extractors via asyncio.to_thread."""
    from mindspace.capture.extractors import extract_url, extract_repo, parse_github_url

    url = resource.source_url

    if resource.type == "repo" and parse_github_url(url):
        data = await asyncio.to_thread(extract_repo, url)
        readme = data.get("readme_text", "") or ""
        return {
            "title": f"{data.get('owner', '')}/{data.get('repo_name', '')}",
            "text": f"{data.get('description', '')}\n\n{readme}",
            "metadata": {k: v for k, v in data.items() if k != "readme_text"},
        }

    data = await asyncio.to_thread(extract_url, url)
    return {
        "title": data.get("title"),
        "text": data.get("extracted_text", ""),
        "metadata": {
            "url": url,
            "author": data.get("author"),
            "word_count": data.get("word_count"),
            "excerpt": data.get("excerpt"),
        },
    }


async def _embed_resource(resource: Resource) -> None:
    """Chunk and embed resource content into ChromaDB."""
    from mindspace.derived.chunker import Chunker
    from mindspace.infra.embedder import Embedder
    from mindspace.infra.vectordb import VectorDB

    text = resource.raw_content
    if not text or not text.strip():
        return

    # Prepend title for better embeddings
    if resource.title:
        text = f"Title: {resource.title}\n\n{text}"

    source_id = f"resource_{resource.id}"
    chunker = Chunker()
    chunks = await asyncio.to_thread(chunker.chunk, text, source_id)

    embedder = Embedder()
    vectordb = VectorDB(collection_name="conversation_chunks")

    for chunk in chunks:
        embedding = await asyncio.to_thread(embedder.embed_one, chunk.text)
        metadata = {
            "type": resource.type,
            "source_id": resource.id,
            "conversation_id": resource.conversation_id or "",
            "source_url": resource.source_url or "",
            "title": resource.title or "",
        }
        await asyncio.to_thread(
            vectordb.upsert,
            ids=[chunk.chunk_id],
            embeddings=[embedding],
            documents=[chunk.text],
            metadatas=[metadata],
        )
