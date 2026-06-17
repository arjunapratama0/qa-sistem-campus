from collections import defaultdict, deque
from time import monotonic
from uuid import uuid4

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings

settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid4()))
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "no-referrer"
        response.headers["permissions-policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["cache-control"] = "no-store"
        return response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        limit = self._limit_for_path(request.url.path)
        if not limit:
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        now = monotonic()
        window_start = now - 60
        bucket = self.requests[key]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
            )

        bucket.append(now)
        return await call_next(request)

    def _limit_for_path(self, path: str) -> int | None:
        if path.endswith("/auth/login") or path.endswith("/auth/register"):
            return settings.rate_limit_auth_per_minute
        if path.endswith("/qa/ask"):
            return settings.rate_limit_qa_per_minute
        return None
