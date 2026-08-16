from typing import List
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Queries Assistant"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
    ]

    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  

    DATABASE_URL: SecretStr

    VECTOR_DB_URL: str = "http://localhost:6333"
    VECTOR_DB_COLLECTION: str = "course_documents_hf"

    GOOGLE_API_KEY: SecretStr
    LLM_MODEL: str = "gemini-3.6-flash"
    LLM_TEMPERATURE: float = 0.0  
    LLM_MAX_TOKENS: int = 2048    
    LLM_TOP_P: float = 0.9        

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384 

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()