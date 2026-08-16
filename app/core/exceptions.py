from app.core.constants import ErrorMessages

class BaseAppException(Exception):
    """Base exception for all custom application errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class NotFoundException(BaseAppException):
    """Raised when a requested resource (User, Course, Document) does not exist."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)

class CredentialsException(BaseAppException):
    """Raised when authentication fails or token is invalid."""
    def __init__(self, message: str = ErrorMessages.INVALID_CREDENTIALS):
        super().__init__(message)

class PermissionDeniedException(BaseAppException):
    """Raised when a user lacks access rights to a resource."""
    def __init__(self, message: str = ErrorMessages.INSUFFICIENT_PERMISSIONS):
        super().__init__(message)

class BadRequestException(BaseAppException):
    """Raised for malformed requests or invalid business logic state."""
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message)

class DocumentProcessingException(BaseAppException):
    """Raised when the PDF ingestion or chunking pipeline fails."""
    def __init__(self, message: str = "An error occurred while processing the document."):
        super().__init__(message)

class VectorDBException(BaseAppException):
    """Raised when Qdrant fails to connect, upload, or retrieve data."""
    def __init__(self, message: str = ErrorMessages.VECTOR_DB_ERROR):
        super().__init__(message)

class LLMException(BaseAppException):
    """Raised when the LLM provider fails."""
    def __init__(self, message: str = ErrorMessages.LLM_GENERATION_FAILED):
        super().__init__(message)