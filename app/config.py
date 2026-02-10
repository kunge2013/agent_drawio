"""Application configuration using Pydantic settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "DrawIO Agent"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:your_password@localhost:3306/drawio_agent"

    # OpenAI/LangChain
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    OPENAI_MODEL: str = "qwen-plus"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 4000

    # DrawIO Export
    DRAWIO_EXPORT_DIR: str = "./exports"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
