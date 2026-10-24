"""Shared test setup: run offline by default, opt into real services with --live.

Offline (default, `uv run pytest`):
    - Settings get dummy values, so no .env or API key is needed.
    - Calls to OpenAI, Postgres, Redis and Celery are replaced with fakes.
    - Tests marked `live` are skipped.

Live (`uv run pytest --live`):
    - Settings come from your .env / environment as usual.
    - Tests marked `live` run against the real services.
    - Unmarked tests still use the fakes.
"""
from typing import Any

import pytest

FAKE_LLM_ANSWER = "Fake LLM answer (offline test run)"

# Forced (not setdefault) so a real key in the shell or .env never leaks into
# an offline run. Environment variables take precedence over .env in Settings.
OFFLINE_ENV = {
    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
    "OPENAI_API_KEY": "sk-test-offline",
    "VALID_TOKENS": "test_token",
    "JWT_SECRET_KEY": "test-secret-key-for-offline-runs-only",
    "DEBUG": "false",
    "REDIS_URL": "redis://localhost:6379/0",
    "CELERY_BROKER_URL": "memory://",
    "CELERY_RESULT_BACKEND": "cache+memory://",
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="run tests marked 'live' against real OpenAI/Postgres/Redis/Docker",
    )


def pytest_configure(config: pytest.Config) -> None:
    # Runs before test modules are imported, i.e. before Settings() is built.
    if not config.getoption("--live"):
        import os

        os.environ.update(OFFLINE_ENV)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(reason="needs real services; run with --live")
    for item in items:
        if item.get_closest_marker("live"):
            item.add_marker(skip_live)


class _FakeTask:
    """Stands in for a Celery task: .delay() returns an object with an id."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id

    def delay(self, *args: Any, **kwargs: Any) -> Any:
        return type("FakeAsyncResult", (), {"id": self.task_id})()


class _FakeAsyncResult:
    """Stands in for celery.result.AsyncResult of a task nobody has run."""

    state = "PENDING"
    info = None
    result = None

    def __init__(self, task_id: str, app: Any = None) -> None:
        self.id = task_id

    def ready(self) -> bool:
        return False


@pytest.fixture(autouse=True)
def offline_services(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace every external call with a fake, unless the test is marked live.

    Tests can still patch these themselves (e.g. with @patch); their patch wins.
    """
    if request.node.get_closest_marker("live"):
        return

    from app.api import ask_question, router
    from app.api.helpers import health_check

    # LLM + embeddings + pgvector: classify everything as IT, never find a
    # local match, and answer with a fixed string.
    monkeypatch.setattr(ask_question.ai_router, "classify_question", lambda question: "it")
    monkeypatch.setattr(ask_question, "find_best_match", lambda question, threshold=None: None)
    monkeypatch.setattr(ask_question, "get_openai_answer", lambda question: FAKE_LLM_ANSWER)

    # Celery
    monkeypatch.setattr(router, "generate_embeddings_task", _FakeTask("fake-generate-task"))
    monkeypatch.setattr(router, "update_embeddings_task", _FakeTask("fake-update-task"))
    monkeypatch.setattr(router, "AsyncResult", _FakeAsyncResult)

    # Health checks behind /health (tests that call the check functions
    # directly import the originals, so they are unaffected).
    monkeypatch.setattr(
        health_check,
        "check_database_connection",
        lambda: {"status": "connected", "connection": "successful", "pgvector_available": True},
    )
    monkeypatch.setattr(
        health_check,
        "check_embeddings_status",
        lambda: {"status": "loaded", "embeddings_count": 1, "has_embeddings": True},
    )
    monkeypatch.setattr(health_check, "check_redis_connection", lambda: {"status": "healthy"})
    monkeypatch.setattr(health_check, "check_celery_worker", lambda: {"status": "healthy"})
