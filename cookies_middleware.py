# middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class CookiesMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.set_cookie(key="session_id", value="unique_session_id")
        return response
