"""Conversation model."""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Conversation(Base):
    """Conversation model for storing chat sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(
        Enum("active", "archived", "deleted", name="conversation_status"),
        default="active"
    )

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    designs = relationship("Design", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
    )
