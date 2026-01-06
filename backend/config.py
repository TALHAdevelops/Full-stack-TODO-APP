from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve backend directory for optional local .env usage during development
BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"

_settings_config = {"extra": "ignore"}
if ENV_FILE.exists():
    _settings_config["env_file"] = str(ENV_FILE)
    _settings_config["env_file_encoding"] = "utf-8"


class Settings(BaseSettings):
    """Application settings from environment variables"""

    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(**_settings_config)

    @property
    def cors_origins(self) -> List[str]:
        """Return sanitized CORS origins list."""
        raw_origins = [origin.strip() for origin in self.FRONTEND_URL.split(",")]
        return [origin for origin in raw_origins if origin]


settings = Settings()
