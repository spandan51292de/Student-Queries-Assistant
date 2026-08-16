from enum import Enum

class DocumentStatus(str, Enum):
    """States for the document ingestion pipeline."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ChatRole(str, Enum):
    """Standardized roles for conversational memory."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ErrorMessages:
    """Standardized error messages for exceptions and user feedback."""
    USER_NOT_FOUND = "The requested user does not exist."
    COURSE_NOT_FOUND = "The requested course could not be found."
    DOCUMENT_NOT_FOUND = "The document could not be found."
    INVALID_CREDENTIALS = "Could not validate credentials."
    INSUFFICIENT_PERMISSIONS = "You do not have permission to perform this action."
    LLM_GENERATION_FAILED = "The AI assistant failed to generate a response."
    VECTOR_DB_ERROR = "Failed to communicate with the vector database."

class AppConstants:
    """General application-wide constants."""
    MAX_UPLOAD_SIZE_MB = 10
    ALLOWED_FILE_TYPES = ["application/pdf"]
    DEFAULT_PAGINATION_LIMIT = 20