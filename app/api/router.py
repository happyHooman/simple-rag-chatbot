"""API router for all endpoints."""
from typing import Any

from fastapi import APIRouter, Depends

from ..models import AskQuestionRequest, AskQuestionResponse
from .ask_question import ask_question_service
from .embeddings import generate_embeddings, update_embeddings
from .helpers.auth import get_token
from .helpers.health_check import get_comprehensive_health

# Create router for all API endpoints
router = APIRouter()


@router.get("/")
async def root(token: str = Depends(get_token)) -> dict[str, str]:
    """Root endpoint that returns a welcome message."""
    return {"message": "Hello World"}


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Comprehensive health check endpoint (public - no auth required)."""
    return get_comprehensive_health()


@router.post("/ask-question", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest, token: str = Depends(get_token)) -> AskQuestionResponse:
    """Ask a question and get an answer from local or external sources using LangChain pipeline."""
    return ask_question_service(request)


@router.post("/generate-embeddings")
async def generate_embeddings_endpoint(token: str = Depends(get_token)) -> dict[str, Any]:
    """Generate embeddings for FAQ questions and store them in the database."""
    return generate_embeddings()


@router.post("/update-embeddings")
async def update_embeddings_endpoint(token: str = Depends(get_token)) -> dict[str, Any]:
    """Update embeddings by comparing with existing data."""
    return update_embeddings()



