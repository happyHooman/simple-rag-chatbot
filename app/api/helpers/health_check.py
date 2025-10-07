import subprocess
from datetime import UTC, datetime
from typing import Any

from psycopg2 import OperationalError

from ...config import settings
from ...sql_queries import HEALTH_CHECK_PGVECTOR, HEALTH_CHECK_PING
from ..embeddings import get_db_cursor, get_embeddings_count


def check_docker_container() -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=embeddings_db", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            return {"status": "running", "container_status": status, "running": "Up" in status}

        return {"status": "stopped", "container_status": "Not running", "running": False}

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        return {"status": "error", "container_status": f"Error checking container: {str(e)}", "running": False}


def check_database_connection() -> dict[str, Any]:
    try:
        if not settings.DATABASE_URL:
            return {"status": "error", "message": "DATABASE_URL not configured"}

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(HEALTH_CHECK_PING)
            cursor.fetchone()

            cursor.execute(HEALTH_CHECK_PGVECTOR)
            vector_extension = cursor.fetchone()

        return {
            "status": "connected",
            "connection": "successful",
            "pgvector_available": vector_extension is not None,
            "database": "faq_embeddings"
        }

    except OperationalError as e:
        return {"status": "disconnected", "connection": "failed", "error": str(e)}
    except Exception as e:
        return {"status": "error", "connection": "error", "error": str(e)}


def check_embeddings_status() -> dict[str, Any]:
    try:
        embeddings_count = get_embeddings_count()
        has_embeddings = embeddings_count > 0

        return {
            "status": "loaded" if has_embeddings else "empty",
            "embeddings_count": embeddings_count,
            "has_embeddings": has_embeddings,
        }
    except Exception as e:
        return {"status": "error", "embeddings_count": 0, "error": str(e)}


def get_comprehensive_health() -> dict[str, Any]:
    docker_status = check_docker_container()
    database_status = check_database_connection()
    embeddings_status = check_embeddings_status()

    services_operational = all((
        docker_status.get("status") == "running",
        database_status.get("status") == "connected",
        embeddings_status.get("status") in ("loaded", "empty"),
    ))

    return {
        "overall_status": "operational" if services_operational else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {
            "docker": docker_status,
            "database": database_status,
            "embeddings": embeddings_status,
        },
        "summary": {
            "docker_running": docker_status.get("running", False),
            "database_connected": database_status.get("status") == "connected",
            "embeddings_ready": embeddings_status.get("has_embeddings", False),
        },
    }
