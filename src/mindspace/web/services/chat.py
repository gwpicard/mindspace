"""Chat service — Claude conversation with streaming."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.infra.config import get_settings
from mindspace.web.db.models import Message

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a thoughtful AI assistant in Mindspace, a personal intelligence system. \
You help the user capture, explore, and connect their ideas. \
Be concise but substantive. When the user shares a link or resource, acknowledge it and \
offer to discuss its content once processed. \
When the user thinks out loud, engage genuinely — ask clarifying questions, \
surface connections, and help refine ideas. \
Keep responses focused and avoid unnecessary filler."""

CONTEXT_WINDOW_SIZE = 30


class ChatService:
    """Handles streaming chat with Claude."""

    def __init__(self, client: anthropic.AsyncAnthropic | None = None) -> None:
        settings = get_settings()
        if not client and not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured. Add it to your .env file.")
        self._client = client or anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_model

    async def get_context_messages(
        self, conversation_id: str, db: AsyncSession
    ) -> list[dict[str, str]]:
        """Load the last N messages for context."""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(CONTEXT_WINDOW_SIZE)
        )
        messages = list(reversed(result.scalars().all()))
        return [{"role": m.role, "content": m.content} for m in messages]

    async def stream_response(
        self,
        conversation_id: str,
        user_content: str,
        db: AsyncSession,
    ) -> AsyncGenerator[str, None]:
        """Stream Claude's response, yielding text chunks."""
        context = await self.get_context_messages(conversation_id, db)
        # Add the new user message to context
        context.append({"role": "user", "content": user_content})

        async with self._client.messages.stream(
            model=self._model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=context,
        ) as stream:
            async for text in stream.text_stream:
                yield text
