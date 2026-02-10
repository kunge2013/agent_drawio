"""Message schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MessageRequest(BaseModel):
    """Request schema for sending a message."""

    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    conversation_id: Optional[int] = Field(None, description="Conversation ID (optional for new conversations)")


class MessageResponse(BaseModel):
    """Response schema for message responses."""

    message_id: int
    conversation_id: int
    message: str
    generated_content: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    title: Optional[str] = Field(None, max_length=255, description="Conversation title")


class ConversationResponse(BaseModel):
    """Response schema for conversation data."""

    id: int
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True
