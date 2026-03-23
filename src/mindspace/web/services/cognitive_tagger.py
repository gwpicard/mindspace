"""Cognitive operation tagging via Claude."""

from __future__ import annotations

import json
import logging

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.infra.config import get_settings
from mindspace.web.db.models import Message

logger = logging.getLogger(__name__)

COGNITIVE_OPS = [
    "exploring",
    "synthesising",
    "questioning",
    "reacting",
    "connecting",
    "wondering",
    "revisiting",
    "explaining",
    "compressing",
    "expanding",
    "reflecting",
]

CLASSIFICATION_PROMPT = f"""Classify the cognitive operations present in the following message. \
Return ONLY a JSON array of strings from this list: {json.dumps(COGNITIVE_OPS)}.

A message can have multiple operations. Return an empty array if none clearly apply. \
Do not explain, just return the JSON array.

Message: {{text}}"""


async def tag_message(message_id: str, db: AsyncSession) -> None:
    """Tag a message with cognitive operations."""
    msg = await db.get(Message, message_id)
    if msg is None or msg.role != "user":
        return

    if msg.cognitive_operations:
        return  # already tagged

    settings = get_settings()
    if not settings.anthropic_api_key:
        return

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(text=msg.content[:1000]),
            }],
        )

        raw = response.content[0].text.strip()
        try:
            ops = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid JSON from cognitive tagger for %s: %s", message_id, raw[:200])
            return
        if not isinstance(ops, list):
            return
        ops = [op for op in ops if op in COGNITIVE_OPS]

        msg.cognitive_operations = json.dumps(ops)
        await db.commit()
        logger.debug("Tagged message %s: %s", message_id, ops)

    except Exception as e:
        logger.warning("Cognitive tagging failed for %s: %s", message_id, e)
