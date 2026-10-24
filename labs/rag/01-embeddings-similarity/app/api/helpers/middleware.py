import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...config.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"{request.method} {request.url.path} - Error ({process_time:.3f}s): {str(e)}", exc_info=True)
            raise
