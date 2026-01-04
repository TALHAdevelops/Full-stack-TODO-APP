import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BACKEND_DIR, ".env")

class Settings(BaseSettings):
    """Application settings from environment variables"""
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

settings = Settings()
