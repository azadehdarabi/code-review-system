from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    local_model_path: Optional[str] = None
    local_model_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env" 