from fastapi import Request
import logging
import json
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: logging.Logger = None, max_len: int = 10000):
        super().__init__(app)
        self.logger = logger or logging.getLogger("drl-learning-engine")
        self.max_len = max_len

    async def dispatch(self, request: Request, call_next):
        # Read the body (may be empty). We will re-inject it so the endpoint can still read it.
        try:
            body_bytes = await request.body()
        except Exception as e:
            self.logger.exception("Failed to read request body: %s", e)
            body_bytes = b""

        # Prepare a safe, truncated representation for logs
        try:
            display_bytes = body_bytes[: self.max_len]
            try:
                text = display_bytes.decode("utf-8")
                try:
                    # Pretty-print JSON bodies when possible
                    parsed = json.loads(text)
                    pretty = json.dumps(parsed, ensure_ascii=False)
                except Exception:
                    pretty = text
            except Exception:
                pretty = repr(display_bytes)

            if len(body_bytes) > self.max_len:
                pretty += "... (truncated)"

            self.logger.info("Incoming request: %s %s body: %s", request.method, request.url.path, pretty)
        except Exception:
            self.logger.exception("Failed to prepare request body log")

        # Re-inject body for downstream consumers by replacing the receive coroutine
        async def receive() -> dict:
            # small await to satisfy linters that expect async functions to use await
            await asyncio.sleep(0)
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request._receive = receive

        response = await call_next(request)
        return response


def register_logging_middleware(app, logger_name: str = "drl-learning-engine", max_len: int = 10000):
    """Configure logger and attach the LoggingMiddleware to the FastAPI app."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(logger_name)
    app.add_middleware(LoggingMiddleware, logger=logger, max_len=max_len)
