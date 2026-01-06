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
    VERCEL_URL: str = ""  # Vercel provides this in production

    model_config = SettingsConfigDict(**_settings_config)

    @property
    def cors_origins(self) -> List[str]:
        """Return sanitized CORS origins list including production Vercel domain."""
        raw_origins = [origin.strip() for origin in self.FRONTEND_URL.split(",")]

        # Add Vercel production URL if available
        if self.VERCEL_URL:
            vercel_prod_url = f"https://{self.VERCEL_URL}"
            if vercel_prod_url not in raw_origins:
                raw_origins.append(vercel_prod_url)

        # Also allow any Vercel preview URL pattern
        raw_origins.append("https://*.vercel.app")

        return [origin for origin in raw_origins if origin]


settings = Settings()
