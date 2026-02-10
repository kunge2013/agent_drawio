"""Design and diagram schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DesignResponse(BaseModel):
    """Response schema for design data."""

    id: int
    conversation_id: int
    name: str
    description: Optional[str] = None
    prototype_data: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiagramResponse(BaseModel):
    """Response schema for diagram data."""

    id: int
    design_id: int
    diagram_type: str
    title: str
    flow_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """Request schema for exporting diagrams."""

    diagram_id: int = Field(..., description="Diagram ID to export")


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = "healthy"
    version: str = "1.0.0"
