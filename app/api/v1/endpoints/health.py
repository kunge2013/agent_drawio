"""Health check endpoint."""
from fastapi import APIRouter
from app.schemas.design import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
