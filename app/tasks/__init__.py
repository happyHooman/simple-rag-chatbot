"""Celery tasks package."""
from .embeddings_tasks import (
    generate_embeddings_task,
    update_embeddings_task,
)

__all__ = [
    "generate_embeddings_task",
    "update_embeddings_task",
]

