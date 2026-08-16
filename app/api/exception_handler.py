from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    CredentialsException,
    PermissionDeniedException,
    BadRequestException,
    DocumentProcessingException,
    VectorDBException,
    LLMException
)

logger = logging.getLogger(__name__)

async def custom_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Translates pure Python domain exceptions into FastAPI HTTP responses.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, CredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDeniedException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, BadRequestException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, VectorDBException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, LLMException):
        status_code = status.HTTP_502_BAD_GATEWAY
    elif isinstance(exc, DocumentProcessingException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if status_code >= 500:
        logger.error(f"Server Error: {exc.message}", exc_info=True)
    else:
        logger.warning(f"Client Error: {exc.message}")

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.message
        },
    )

def register_exception_handlers(app) -> None:
    """
    Registers the custom exception handlers with the FastAPI application.
    """
    app.add_exception_handler(BaseAppException, custom_app_exception_handler)