from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AS_AUTHORIZATION_ENDPOINT: str
    AS_TOKEN_ENDPOINT: str

    LOGIN_CLIENT_ID: str
    LOGIN_CLIENT_SECRET: str
    LOGIN_REDIRECT_URI: str

    BACKEND_URL: str
    ENVIRONMENT: str = "local"

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    SESSION_SECRET_KEY: str = ""

    FRONTEND_URL: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
