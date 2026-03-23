"""SQLAlchemy ORM models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# Many-to-many: conversations <-> channels
conversation_channels = Table(
    "conversation_channels",
    Base.metadata,
    Column("conversation_id", String, ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True),
    Column("channel_id", String, ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True),
)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    resources = relationship("Resource", back_populates="conversation", cascade="all, delete-orphan")
    channels = relationship("Channel", secondary=conversation_channels, back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    cognitive_operations = Column(Text, nullable=True)  # JSON array
    is_embedded = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="messages")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # "url", "repo", "snippet", "video"
    source_url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    raw_content = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON object
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    message_id = Column(String, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    is_embedded = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="resources")


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversations = relationship("Conversation", secondary=conversation_channels, back_populates="channels")
