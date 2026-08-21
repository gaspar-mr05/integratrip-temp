import logging
from datetime import datetime, timedelta, timezone

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

TABLE = "oauth_mcp_state"
STATE_TTL = timedelta(minutes=10)


def insert_mcp_state(user_id: str, mcp_server_id: str, state: str, code_verifier: str) -> bool:
    expires_at = datetime.now(timezone.utc) + STATE_TTL
    try:
        result = (
            get_supabase_client()
            .table(TABLE)
            .insert(
                {
                    "user_id": user_id,
                    "mcp_server_id": mcp_server_id,
                    "state": state,
                    "code_verifier": code_verifier,
                    "expires_at": expires_at.isoformat(),
                }
            )
            .execute()
        )
        return bool(result.data)
    except Exception:
        logger.exception("Error insertando %s", TABLE)
        return False


def consume_mcp_state(state: str) -> dict | None:
    result = (
        get_supabase_client()
        .table(TABLE)
        .delete()
        .eq("state", state)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]
