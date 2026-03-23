"""Embed conversation messages into ChromaDB."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.web.db.models import Message

logger = logging.getLogger(__name__)


async def embed_unembedded_messages(db: AsyncSession) -> int:
    """Embed all messages not yet embedded. Returns count embedded."""
    result = await db.execute(
        select(Message).where(Message.is_embedded == False).order_by(Message.created_at)
    )
    messages = result.scalars().all()
    if not messages:
        return 0

    from mindspace.derived.chunker import Chunker
    from mindspace.infra.embedder import Embedder
    from mindspace.infra.vectordb import VectorDB

    chunker = Chunker()
    embedder = Embedder()
    vectordb = VectorDB(collection_name="conversation_chunks")

    count = 0
    for msg in messages:
        if not msg.content.strip():
            msg.is_embedded = True
            continue

        source_id = f"msg_{msg.id}"
        text = f"[{msg.role}] {msg.content}"
        chunks = await asyncio.to_thread(chunker.chunk, text, source_id)

        for chunk in chunks:
            embedding = await asyncio.to_thread(embedder.embed_one, chunk.text)
            metadata = {
                "type": "message",
                "role": msg.role,
                "message_id": msg.id,
                "conversation_id": msg.conversation_id,
            }
            await asyncio.to_thread(
                vectordb.upsert,
                ids=[chunk.chunk_id],
                embeddings=[embedding],
                documents=[chunk.text],
                metadatas=[metadata],
            )

        msg.is_embedded = True
        count += 1

    await db.commit()
    logger.info("Embedded %d messages", count)
    return count
