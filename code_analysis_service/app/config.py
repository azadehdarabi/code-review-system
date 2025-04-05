from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    llm_service_url: str = "http://llm-service:8000"
    redis_url: str = "redis://redis:6379/0"
    repo_storage_path: str = "/repos"
    
    class Config:
        env_file = ".env" 