"""
Core configuration settings for the AI Callcenter Agent MVP.
Designer: Abdullah Alawiss
"""

from typing import Any, Dict, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    PROJECT_NAME: str = "AI Callcenter Agent MVP"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "callcenter_db"
    POSTGRES_PORT: str = "5432"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "callcenter-audio"
    MINIO_SECURE: bool = False
    
    # Audio Processing
    MAX_AUDIO_DURATION: int = 3600  # 1 hour in seconds
    SUPPORTED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a", "flac"]
    WHISPER_MODEL: str = "medium"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # SFTP Configuration
    SFTP_HOST: Optional[str] = None
    SFTP_PORT: int = 22
    SFTP_USERNAME: Optional[str] = None
    SFTP_PASSWORD: Optional[str] = None
    SFTP_REMOTE_PATH: str = "/incoming"
    
    # GDPR Settings
    ENABLE_DATA_REDACTION: bool = True
    REDACTION_LANGUAGE: str = "no"  # Norwegian
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
