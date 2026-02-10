"""Message model."""
from sqlalchemy import Column, Integer, Text, DateTime, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Message(Base):
    """Message model for storing chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    role = Column(
        Enum("user", "assistant", "system", name="message_role"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_conversation_id", "conversation_id"),
        Index("idx_created_at", "created_at"),
    )
