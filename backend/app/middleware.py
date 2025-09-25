import logging
import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions to let FastAPI handle them
            raise
        except Exception as e:
            # Log the full traceback
            logger.error(f"Unhandled error in {request.method} {request.url}: {e}")
            logger.error(traceback.format_exc())
            
            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "timestamp": time.time()
                }
            )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f" {request.method} {request.url.path} - Start")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f" {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Simple rate limiting by IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Reset counts every minute
        if current_time - self.last_reset > 60:
            self.request_counts = {}
            self.last_reset = current_time
        
        # Check rate limit
        current_count = self.request_counts.get(client_ip, 0)
        if current_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} per minute"
                }
            )
        
        # Increment count
        self.request_counts[client_ip] = current_count + 1
        
        response = await call_next(request)
        return response