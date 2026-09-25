from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", BACKEND_DIR / ".env.local"),
        extra="ignore",
    )

    AS_AUTHORIZATION_ENDPOINT: str
    AS_TOKEN_ENDPOINT: str

    LOGIN_CLIENT_ID: str
    LOGIN_CLIENT_SECRET: str

    BACKEND_URL: str
    PUBLIC_API_URL: str
    ENVIRONMENT: str = "local"

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_HTTP2_ENABLED: bool = False
    SUPABASE_HTTP_TIMEOUT_SECONDS: float = Field(default=120, gt=0)

    SESSION_SECRET_KEY: str = Field(min_length=32)

    FRONTEND_URL: str

    LLM_GRPC_TARGET: str = Field(default="dns:///iic3103-tarea2-llm-z2fqxmm2ja-uc.a.run.app:443")
    LLM_GRPC_TLS: bool = Field(default=True)
    LLM_GRPC_TIMEOUT_SECONDS: float = Field(default=30, gt=0)
    LLM_STUDENT_EMAIL: str
    LLM_STUDENT_ID: str

    @property
    def login_redirect_uri(self) -> str:
        return f"{self.PUBLIC_API_URL.rstrip('/')}/auth/callback"

    def mcp_redirect_uri(self, server_name: str) -> str:
        return f"{self.PUBLIC_API_URL.rstrip('/')}/mcp/{server_name}/callback"

    @property
    def client_metadata_url(self) -> str:
        return f"{self.PUBLIC_API_URL.rstrip('/')}/.well-known/oauth-client-metadata.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
