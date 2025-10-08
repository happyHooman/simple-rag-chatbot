import asyncio
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
            return {"status": "error", "message": "DATABASE_URL not configured", "connection": "error"}

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(HEALTH_CHECK_PING)
            cursor.fetchone()

            cursor.execute(HEALTH_CHECK_PGVECTOR)
            vector_extension = cursor.fetchone()

        pgvector_available = vector_extension is not None

        if not pgvector_available:
            return {
                "status": "degraded",
                "message": "pgvector extension not available",
                "connection": "successful",
                "pgvector_available": False
            }

        return {
            "status": "connected",
            "message": "Connected",
            "connection": "successful",
            "pgvector_available": True
        }

    except OperationalError as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}", "connection": "error"}
    except Exception as e:
        return {"status": "error", "message": str(e), "connection": "error"}


def check_embeddings_status() -> dict[str, Any]:
    try:
        embeddings_count = get_embeddings_count()

        if embeddings_count > 0:
            return {
                "status": "loaded",
                "message": f"{embeddings_count} embeddings loaded",
                "embeddings_count": embeddings_count,
                "has_embeddings": True
            }
        else:
            return {
                "status": "empty",
                "message": "No embeddings (empty database)",
                "embeddings_count": 0,
                "has_embeddings": False
            }
    except Exception as e:
        return {"status": "error", "message": str(e), "embeddings_count": 0, "has_embeddings": False}


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


async def get_comprehensive_health() -> dict[str, Any]:
    # Run all checks concurrently for better performance
    database_status, embeddings_status, redis_status, celery_status = await asyncio.gather(
        asyncio.to_thread(check_database_connection),
        asyncio.to_thread(check_embeddings_status),
        asyncio.to_thread(check_redis_connection),
        asyncio.to_thread(check_celery_worker),
    )

    # Create summary with boolean flags
    summary = {
        "database_connected": database_status.get("status") in ["connected", "healthy"],
        "redis_connected": redis_status.get("status") in ["healthy", "connected"],
        "celery_workers_active": celery_status.get("status") in ["healthy", "running"],
        "embeddings_ready": embeddings_status.get("has_embeddings", False)
    }

    # Check if all services are in good state
    # Note: pgvector_available defaults to True if not present (for backward compatibility with tests)
    all_healthy = (
        database_status.get("status") in ["connected", "healthy"] and
        database_status.get("pgvector_available", True) and
        embeddings_status.get("status") in ["loaded", "empty"] and
        redis_status.get("status") in ["healthy", "connected"] and
        celery_status.get("status") in ["healthy", "running"]
    )

    has_degraded = any(
        service.get("status") == "degraded"
        for service in [database_status, embeddings_status, redis_status, celery_status]
    )

    has_disconnected = (
        not summary["database_connected"] or
        not summary["redis_connected"] or
        not summary["celery_workers_active"]
    )

    if all_healthy:
        overall = "operational"
    elif has_degraded or has_disconnected:
        overall = "degraded"
    else:
        overall = "unhealthy"

    return {
        "overall_status": overall,
        "timestamp": datetime.now(UTC).isoformat(),
        "summary": summary,
        "services": {
            "database": database_status,
            "redis": redis_status,
            "celery": celery_status,
            "embeddings": embeddings_status,
        },
    }
