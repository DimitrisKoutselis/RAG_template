import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    def __init__(self, app, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("rag_template.http")

    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        start_time = time.time()

        self.logger.info(
            f"Request: {request.method} {request.url.path}"
        )

        response = await call_next(request)

        duration = time.time() - start_time

        self.logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Duration: {duration:.3f}s"
        )

        return response
