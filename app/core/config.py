from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "Student Queries Assistant"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    # Relational Database (PostgreSQL)
    DATABASE_URL: str

    # Vector Database (Qdrant)
    VECTOR_DB_URL: str = "http://localhost:6333"

    # LLM Provider (Using Google's Free Tier)
    GOOGLE_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()