"""Design model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Design(Base):
    """Design model for storing generated designs."""

    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    prototype_data = Column(JSON)  # Stores prototype design data
    documentation = Column(Text)  # Stores markdown documentation
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="designs")
    diagrams = relationship("Diagram", back_populates="design", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_conversation_id", "conversation_id"),
    )
