"""Vigencia de las filas de state de un flujo OAuth (login y conexión MCP)."""

from datetime import datetime, timezone


def is_state_expired(expires_at: str) -> bool:
    expiration = datetime.fromisoformat(expires_at)
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    return expiration <= datetime.now(timezone.utc)
