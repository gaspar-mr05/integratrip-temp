import logging
from datetime import datetime, timedelta, timezone

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def upsert_mcp_connection(
    *,
    user_id: str,
    mcp_server_id: str,
    access_token: str,
    refresh_token: str | None,
    expires_in: int | None,
    scope: str | None,
) -> dict | None:
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=expires_in) if expires_in is not None else None

    try:
        result = (
            supabase.table("mcp_connections")
            .upsert(
                {
                    "user_id": user_id,
                    "mcp_server_id": mcp_server_id,
                    "access_token_enc": access_token,
                    "refresh_token_enc": refresh_token,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "scope": scope,
                    "status": "active",
                    "updated_at": now.isoformat(),
                },
                on_conflict="user_id,mcp_server_id",
            )
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        logger.exception(
            "Error guardando mcp_connection para user_id=%s mcp_server_id=%s",
            user_id,
            mcp_server_id,
        )
        return None


def get_mcp_connection(user_id: str, mcp_server_id: str) -> dict | None:
    supabase = get_supabase_client()
    result = (
        supabase.table("mcp_connections")
        .select("*")
        .eq("user_id", user_id)
        .eq("mcp_server_id", mcp_server_id)
        .execute()
    )
    return result.data[0] if result.data else None
