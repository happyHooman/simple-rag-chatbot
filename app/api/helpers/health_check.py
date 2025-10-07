from datetime import UTC, datetime
from typing import Any

import redis
from celery import Celery
from psycopg2 import OperationalError

from ...config import settings
from ...sql_queries import HEALTH_CHECK_PGVECTOR, HEALTH_CHECK_PING
from ..embeddings import get_db_cursor, get_embeddings_count


def check_database_connection() -> dict[str, Any]:
    try:
        if not settings.DATABASE_URL:
            return {"status": "error", "message": "DATABASE_URL not configured"}

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(HEALTH_CHECK_PING)
            cursor.fetchone()

            cursor.execute(HEALTH_CHECK_PGVECTOR)
            vector_extension = cursor.fetchone()

        if vector_extension is None:
            return {"status": "degraded", "message": "pgvector extension not available"}

        return {"status": "healthy", "message": "Connected"}

    except OperationalError as e:
        return {"status": "unhealthy", "message": f"Connection failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_embeddings_status() -> dict[str, Any]:
    try:
        embeddings_count = get_embeddings_count()

        if embeddings_count > 0:
            return {"status": "healthy", "message": "Embeddings loaded"}
        else:
            return {"status": "healthy", "message": "No embeddings (empty database)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_redis_connection() -> dict[str, Any]:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        redis_client.ping()
        return {"status": "healthy", "message": "Connected"}
    except redis.ConnectionError:
        return {"status": "unhealthy", "message": "Connection refused"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_celery_worker() -> dict[str, Any]:
    try:
        celery_app = Celery(broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
        inspect = celery_app.control.inspect(timeout=5)
        active_workers = inspect.active()

        if active_workers:
            return {"status": "healthy", "message": "Workers active"}
        else:
            return {"status": "degraded", "message": "No workers available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_comprehensive_health() -> dict[str, Any]:
    database_status = check_database_connection()
    embeddings_status = check_embeddings_status()
    redis_status = check_redis_connection()
    celery_status = check_celery_worker()

    all_healthy = all(
        service.get("status") == "healthy"
        for service in [database_status, embeddings_status, redis_status, celery_status]
    )

    has_degraded = any(
        service.get("status") == "degraded"
        for service in [database_status, embeddings_status, redis_status, celery_status]
    )

    if all_healthy:
        overall = "healthy"
    elif has_degraded:
        overall = "degraded"
    else:
        overall = "unhealthy"

    return {
        "status": overall,
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {
            "database": database_status,
            "redis": redis_status,
            "celery": celery_status,
            "embeddings": embeddings_status,
        },
    }
