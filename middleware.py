import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(filename='api_requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"Request - Method: {request.method}, Path: {request.url.path}")
        response = await call_next(request)
        logging.info(f"Response - Status Code: {response.status_code}")
        return response
