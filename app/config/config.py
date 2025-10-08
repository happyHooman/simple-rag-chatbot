from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # API Configuration
    API_TITLE: str = "RebelDot Chatbot"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FAQ Chatbot API"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = "INFO"

    # Database Configuration (Required)
    DATABASE_URL: str

    # OpenAI Configuration (Required)
    OPENAI_API_KEY: str

    # Q&A Service Settings
    SIMILARITY_THRESHOLD: float = 0.5
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_CHAT_TEMPERATURE: float = 0.7

    # Authentication Settings (Required)
    VALID_TOKENS: str
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Redis Configuration (Required)
    REDIS_URL: str

    # Celery Configuration (Required)
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 1800
    CELERY_TASK_SOFT_TIME_LIMIT: int = 1500


settings = Settings()
