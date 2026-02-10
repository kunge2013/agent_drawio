"""FastAPI application entry point for DrawIO Agent."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.api.v1.routes import api_router
from app.config import get_settings

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="DrawIO Agent",
    description="AI-powered prototype and diagram generation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for frontend
static_dir = Path(__file__).parent.parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Root endpoint - serves the main UI."""
    template_path = Path(__file__).parent.parent / "frontend" / "templates" / "index.html"
    if template_path.exists():
        return FileResponse(str(template_path))
    return {"message": "DrawIO Agent API", "docs": "/api/docs"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run application startup tasks."""
    print("Starting DrawIO Agent...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print("API documentation available at /api/docs")
