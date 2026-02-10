"""Design service for managing designs and diagrams."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.design import Design
from app.models.diagram import Diagram


class DesignService:
    """Service for managing designs and diagrams."""

    def __init__(self, db: Session):
        """
        Initialize the design service.

        Args:
            db: Database session
        """
        self.db = db

    def create_design(self, design_data: Dict[str, Any]) -> Design:
        """
        Create a new design.

        Args:
            design_data: Design data dictionary

        Returns:
            Created Design object
        """
        design = Design(**design_data)
        self.db.add(design)
        self.db.commit()
        self.db.refresh(design)
        return design

    def save_diagram(self, diagram_data: Dict[str, Any]) -> Diagram:
        """
        Save a diagram to the database.

        Args:
            diagram_data: Diagram data dictionary

        Returns:
            Created Diagram object
        """
        diagram = Diagram(**diagram_data)
        self.db.add(diagram)
        self.db.commit()
        self.db.refresh(diagram)
        return diagram

    def get_design(self, design_id: int) -> Optional[Design]:
        """
        Get a design by ID.

        Args:
            design_id: Design ID

        Returns:
            Design object or None
        """
        return self.db.query(Design).filter(Design.id == design_id).first()

    def get_diagram(self, diagram_id: int) -> Optional[Diagram]:
        """
        Get a diagram by ID.

        Args:
            diagram_id: Diagram ID

        Returns:
            Diagram object or None
        """
        return self.db.query(Diagram).filter(Diagram.id == diagram_id).first()

    def get_designs_by_conversation(self, conversation_id: int) -> list[Design]:
        """
        Get all designs for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of Design objects
        """
        return self.db.query(Design).filter(
            Design.conversation_id == conversation_id
        ).all()

    def get_diagrams_by_design(self, design_id: int) -> list[Diagram]:
        """
        Get all diagrams for a design.

        Args:
            design_id: Design ID

        Returns:
            List of Diagram objects
        """
        return self.db.query(Diagram).filter(
            Diagram.design_id == design_id
        ).all()
