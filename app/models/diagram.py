"""Diagram model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Diagram(Base):
    """Diagram model for storing generated diagrams."""

    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    design_id = Column(
        Integer,
        ForeignKey("designs.id", ondelete="CASCADE"),
        nullable=False
    )
    diagram_type = Column(
        Enum("ui_flow", "business_flow", "prototype", name="diagram_type"),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    drawio_xml = Column(Text, nullable=False)  # Stores DrawIO XML content
    flow_data = Column(JSON)  # Stores structured flow data
    file_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    design = relationship("Design", back_populates="diagrams")

    __table_args__ = (
        Index("idx_design_id", "design_id"),
        Index("idx_diagram_type", "diagram_type"),
    )
