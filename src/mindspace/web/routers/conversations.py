"""Conversation CRUD and chat endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mindspace.core.ids import generate_id
from mindspace.web.db.models import Conversation, Message
from mindspace.web.deps import get_db

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# --- Schemas ---


class ConversationCreate(BaseModel):
    title: str | None = None
    channel_ids: list[str] | None = None


class ConversationUpdate(BaseModel):
    title: str | None = None
    channel_ids: list[str] | None = None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    cognitive_operations: list[str] | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_message(cls, msg: Message) -> MessageOut:
        cog_ops = None
        if msg.cognitive_operations:
            try:
                cog_ops = json.loads(msg.cognitive_operations)
            except (json.JSONDecodeError, TypeError):
                cog_ops = None
        return cls(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            cognitive_operations=cog_ops,
        )


class ConversationOut(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime
    channel_ids: list[str] = []

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class SendMessage(BaseModel):
    content: str


# --- Routes ---


@router.post("", status_code=201)
async def create_conversation(
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> ConversationOut:
    conv = Conversation(
        id=generate_id(),
        title=body.title,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv, ["channels"])
    return _conv_out(conv)


@router.get("")
async def list_conversations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationOut]:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.channels))
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_conv_out(c) for c in result.scalars().all()]


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    conv = await _load_conversation(conversation_id, db, load_messages=True)
    messages = [MessageOut.from_orm_message(m) for m in conv.messages]
    out = _conv_out(conv)
    return ConversationDetail(**out.model_dump(), messages=messages)


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    body: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
) -> ConversationOut:
    conv = await _load_conversation(conversation_id, db)
    if body.title is not None:
        conv.title = body.title
    if body.channel_ids is not None:
        from mindspace.web.db.models import Channel
        channels = []
        for cid in body.channel_ids:
            ch = await db.get(Channel, cid)
            if ch:
                channels.append(ch)
        conv.channels = channels
    conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(conv, ["channels"])
    return _conv_out(conv)


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: SendMessage,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Send a user message and stream the assistant's response via SSE."""
    # Auto-create conversation if it doesn't exist
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        conv = Conversation(id=conversation_id)
        db.add(conv)
        await db.commit()

    # Save the user message
    user_msg = Message(
        id=generate_id(),
        conversation_id=conversation_id,
        role="user",
        content=body.content,
    )
    db.add(user_msg)
    conv.updated_at = datetime.now(timezone.utc)
    await db.commit()

    # Detect URLs and trigger background resource processing
    from mindspace.web.services.resource_processor import detect_and_process_urls
    from mindspace.web import tasks as task_manager

    result = await detect_and_process_urls(body.content, user_msg.id, conversation_id, db)

    async def event_stream():
        from mindspace.web.services.chat import ChatService
        from mindspace.web.db.engine import get_session_factory

        # Emit duplicate resource events
        for dup in result.duplicates:
            yield f"event: resource_duplicate\ndata: {json.dumps({'id': dup.id, 'url': dup.url, 'title': dup.title, 'conversation_id': dup.conversation_id})}\n\n"

        # Emit resource_detected events
        for res in result.resources:
            yield f"event: resource_detected\ndata: {json.dumps({'id': res.id, 'url': res.source_url, 'type': res.type})}\n\n"

        # Stream Claude's response
        chat = ChatService()
        full_response = []
        try:
            async with get_session_factory()() as stream_db:
                async for chunk in chat.stream_response(conversation_id, body.content, stream_db):
                    full_response.append(chunk)
                    yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            return

        # Save the assistant message
        assistant_content = "".join(full_response)
        async with get_session_factory()() as save_db:
            assistant_msg = Message(
                id=generate_id(),
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
            )
            save_db.add(assistant_msg)
            c = await save_db.get(Conversation, conversation_id)
            if c:
                c.updated_at = datetime.now(timezone.utc)
            await save_db.commit()

            yield f"event: message_complete\ndata: {json.dumps({'id': assistant_msg.id, 'content': assistant_content})}\n\n"

            # Background tasks: title generation, cognitive tagging
            from mindspace.web.services.title_generator import generate_title
            from mindspace.web.services.cognitive_tagger import tag_message

            # Count messages to decide on title generation
            msg_count = await save_db.scalar(
                select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
            )
            if msg_count and msg_count >= 2:
                task_manager.submit(
                    _run_title_gen(conversation_id), name=f"title-{conversation_id}"
                )

            # Tag cognitive operations on user message
            task_manager.submit(
                _run_cog_tag(user_msg.id), name=f"cogtag-{user_msg.id}"
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _run_title_gen(conversation_id: str) -> None:
    from mindspace.web.db.engine import get_session_factory
    from mindspace.web.services.title_generator import generate_title

    async with get_session_factory()() as db:
        await generate_title(conversation_id, db)


async def _run_cog_tag(message_id: str) -> None:
    from mindspace.web.db.engine import get_session_factory
    from mindspace.web.services.cognitive_tagger import tag_message

    async with get_session_factory()() as db:
        await tag_message(message_id, db)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    conv = await _load_conversation(conversation_id, db)
    await db.delete(conv)
    await db.commit()


# --- Helpers ---


async def _load_conversation(
    conversation_id: str,
    db: AsyncSession,
    load_messages: bool = False,
) -> Conversation:
    opts = [selectinload(Conversation.channels)]
    if load_messages:
        opts.append(selectinload(Conversation.messages))
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id).options(*opts)
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


def _conv_out(conv: Conversation) -> ConversationOut:
    return ConversationOut(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        channel_ids=[ch.id for ch in conv.channels] if conv.channels else [],
    )
