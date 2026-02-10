"""SQLAlchemy models."""
from app.models.base import Base, get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.design import Design
from app.models.diagram import Diagram

__all__ = [
    "Base",
    "get_db",
    "engine",  # Available via lazy import
    "User",
    "Conversation",
    "Message",
    "Design",
    "Diagram",
]


# Provide engine via lazy import to avoid database connection on module import
def __getattr__(name):
    if name == "engine":
        from app.models.base import get_engine
        return get_engine()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

