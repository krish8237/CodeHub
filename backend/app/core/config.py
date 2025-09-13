from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/assessment_platform"
    test_database_url: str = "postgresql://postgres:password@localhost:5432/assessment_platform_test"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Email
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: Optional[str] = None
    mail_port: int = 587
    mail_server: Optional[str] = None
    mail_from_name: str = "Assessment Platform"
    
    # Code Execution
    docker_timeout: int = 30
    max_memory_mb: int = 128
    max_cpu_percent: int = 50
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()