"""API router for all endpoints."""
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends

from ..celery_app import celery_app
from ..models import AskQuestionRequest, AskQuestionResponse
from ..tasks.embeddings_tasks import generate_embeddings_task, update_embeddings_task
from .ask_question import ask_question_service
from .helpers.auth import get_token
from .helpers.health_check import get_comprehensive_health

# Create router for all API endpoints
router = APIRouter()


@router.get("/")
async def root(token: str = Depends(get_token)) -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check (public)."""
    return await get_comprehensive_health()


@router.post("/ask-question", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest, token: str = Depends(get_token)) -> AskQuestionResponse:
    """Ask a question and get an AI-powered answer."""
    return ask_question_service(request)


@router.post("/generate-embeddings")
async def generate_embeddings_endpoint(token: str = Depends(get_token)) -> dict[str, Any]:
    """Generate embeddings (background task). Check status at GET /tasks/{task_id}"""
    task = generate_embeddings_task.delay()
    return {"status": "processing", "message": "Embeddings generation started", "task_id": task.id}


@router.post("/update-embeddings")
async def update_embeddings_endpoint(token: str = Depends(get_token)) -> dict[str, Any]:
    """Update embeddings incrementally (background task). Check status at GET /tasks/{task_id}"""
    task = update_embeddings_task.delay()
    return {"status": "processing", "message": "Embeddings update started", "task_id": task.id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, token: str = Depends(get_token)) -> dict[str, Any]:
    """Get status and result of a background task."""
    task_result = AsyncResult(task_id, app=celery_app)

    response: dict[str, Any] = {
        "task_id": task_id,
        "state": task_result.state,
        "ready": task_result.ready(),
    }

    if task_result.state == "PENDING":
        response["status"] = "Task is waiting to be executed or doesn't exist"

    elif task_result.state == "PROGRESS":
        response["status"] = "Task is in progress"
        response["progress"] = task_result.info

    elif task_result.state == "SUCCESS":
        response["status"] = "Task completed successfully"
        response["result"] = task_result.result

    elif task_result.state == "FAILURE":
        response["status"] = "Task failed"
        response["error"] = str(task_result.info)

    else:
        response["status"] = f"Task state: {task_result.state}"
        if task_result.info:
            response["info"] = str(task_result.info)

    return response



