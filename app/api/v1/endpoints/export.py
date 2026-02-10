"""Export endpoints for downloading diagrams."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.diagram import Diagram

router = APIRouter()


@router.get("/drawio/{diagram_id}")
async def export_drawio(
    diagram_id: int,
    db: Session = Depends(get_db)
):
    """
    Export diagram as DrawIO XML file.

    Args:
        diagram_id: Diagram ID to export
        db: Database session

    Returns:
        DrawIO XML file as downloadable response
    """
    diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()

    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")

    # Create a safe filename
    safe_title = diagram.title.replace(" ", "_").replace("/", "_")
    filename = f"{safe_title}.drawio"

    return Response(
        content=diagram.drawio_xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/design/{design_id}/all")
async def export_all_design_diagrams(
    design_id: int,
    db: Session = Depends(get_db)
):
    """
    Export all diagrams for a design (placeholder for ZIP export).

    Args:
        design_id: Design ID
        db: Database session

    Returns:
        All diagrams for the design
    """
    from app.models.design import Design

    design = db.query(Design).filter(Design.id == design_id).first()

    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    diagrams = db.query(Diagram).filter(Diagram.design_id == design_id).all()

    return {
        "design_id": design_id,
        "design_name": design.name,
        "diagrams": [
            {
                "id": d.id,
                "title": d.title,
                "type": d.diagram_type
            }
            for d in diagrams
        ]
    }
