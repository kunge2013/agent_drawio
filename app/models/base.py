"""Base SQLAlchemy model and database session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings

# Create base class for models
Base = declarative_base()

# Global variables for lazy initialization
_engine = None
_SessionLocal = None


def _ensure_initialized():
    """Ensure database engine and session factory are initialized."""
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine, _SessionLocal


def get_engine():
    """Get database engine."""
    return _ensure_initialized()[0]


def get_session_local():
    """Get session local class."""
    return _ensure_initialized()[1]


def get_db() -> Session:
    """
    Dependency for getting database session.

    Yields:
        Database session
    """
    SessionLocal = _ensure_initialized()[1]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Module-level attributes for backward compatibility (lazy evaluation)
def __getattr__(name):
    if name == "engine":
        return get_engine()
    elif name == "SessionLocal":
        return get_session_local()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
