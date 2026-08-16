import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class AppContextMiddleware(BaseHTTPMiddleware):
    """
    Global middleware to handle request tracking, timing, logging, 
    and security headers across the entire FastAPI application.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        request.state.request_id = request_id

        start_time = time.perf_counter()
        
        logger.info(f"--> {request.method} {request.url.path} [ID: {request_id}]")

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"-x- {request.method} {request.url.path} [ID: {request_id}] "
                f"FAILED in {process_time:.4f}s. Error: {str(e)}"
            )
            raise e
        
        process_time = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        logger.info(
            f"<-- {request.method} {request.url.path} [ID: {request_id}] "
            f"- Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        
        return response