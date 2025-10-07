import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings:
    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE") or "RebelDot Chatbot"
    API_VERSION: str = os.getenv("API_VERSION") or "1.0.0"
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION") or "Alexandru Tornea's assignment for RebelDot"

    # Server Configuration
    HOST: str = os.getenv("HOST") or "127.0.0.1"
    PORT: int = int(os.getenv("PORT") or "8000")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: LogLevel = os.getenv("LOG_LEVEL", "INFO").upper()  # type: ignore

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/faq_embeddings"

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or ""

    # Q&A Service Settings
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD") or "0.5")
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini"
    OPENAI_CHAT_TEMPERATURE: float = float(os.getenv("OPENAI_CHAT_TEMPERATURE") or "0.7")

    # Authentication Settings
    VALID_TOKENS: str = os.getenv("VALID_TOKENS") or "test_token,admin_token,production_token"

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL") or "redis://localhost:6379/0"

    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL") or REDIS_URL
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND") or REDIS_URL
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_TIME_LIMIT") or "1800")  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT") or "1500")  # 25 minutes


settings = Settings()
