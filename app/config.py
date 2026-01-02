from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Absolute path anchoring
# __file__ is lab-gamification/app/config.py
# .parent is lab-gamification/app/
# .parent.parent is lab-gamification/
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

# Debugging: Uncomment the line below to see exactly where it looks
# print(f"Looking for .env at: {ENV_PATH} | Exists: {ENV_PATH.exists()}")

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Stomata Labs Gamification"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_JWT_SECRET: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None

    # Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()