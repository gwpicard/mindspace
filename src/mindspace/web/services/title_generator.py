"""Auto-generate conversation titles from initial messages."""

from __future__ import annotations

import logging

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.infra.config import get_settings
from mindspace.web.db.models import Conversation, Message

logger = logging.getLogger(__name__)


async def generate_title(conversation_id: str, db: AsyncSession) -> None:
    """Generate a title from the first few messages and update the conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(4)
    )
    messages = result.scalars().all()
    if len(messages) < 2:
        return

    text = "\n".join(f"{m.role}: {m.content[:300]}" for m in messages)

    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=50,
        messages=[{
            "role": "user",
            "content": f"Generate a short title (3-7 words, no quotes) for this conversation:\n\n{text}",
        }],
    )

    title = response.content[0].text.strip().strip('"\'')

    conv = await db.get(Conversation, conversation_id)
    if conv and not conv.title:
        conv.title = title
        await db.commit()
        logger.info("Generated title for %s: %s", conversation_id, title)
