"""Celery tasks for embeddings generation and updates."""
from typing import Any

from ..api.embeddings import generate_embeddings as _generate_embeddings
from ..api.embeddings import update_embeddings as _update_embeddings
from ..celery_app import celery_app
from ..config.logging_config import get_logger

logger = get_logger(__name__)


@celery_app.task(name="embeddings.generate", bind=True)  # type: ignore[misc]
def generate_embeddings_task(self: Any) -> dict[str, Any]:
    """Generate embeddings for all FAQ questions and store in database."""
    try:
        logger.info(f"Starting embeddings generation task: {self.request.id}")
        result = _generate_embeddings()

        if result["status"] == "success":
            logger.info(f"Task {self.request.id} completed: {result['count']} embeddings")
        else:
            logger.error(f"Task {self.request.id} failed: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}")
        return {"status": "error", "message": f"Task failed: {str(e)}", "count": 0}


@celery_app.task(name="embeddings.update", bind=True)  # type: ignore[misc]
def update_embeddings_task(self: Any) -> dict[str, Any]:
    """Update embeddings incrementally (add/update/remove based on FAQ changes)."""
    try:
        logger.info(f"Starting embeddings update task: {self.request.id}")
        result = _update_embeddings()

        if result["status"] == "success":
            changes = result.get("changes", {})
            logger.info(
                f"Task {self.request.id} completed: "
                f"{changes.get('added', 0)} added, {changes.get('updated', 0)} updated, {changes.get('removed', 0)} removed"
            )
        else:
            logger.error(f"Task {self.request.id} failed: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Task failed: {str(e)}",
            "changes": {"added": 0, "updated": 0, "removed": 0, "total": 0}
        }

