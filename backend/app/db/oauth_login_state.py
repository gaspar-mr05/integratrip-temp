from datetime import datetime, timedelta, timezone

from app.db.supabase_client import get_supabase_client

TABLE = "oauth_login_state"
STATE_TTL = timedelta(minutes=10)


def insert_login_state(state: str, code_verifier: str) -> bool:
    expires_at = datetime.now(timezone.utc) + STATE_TTL
    result = (
        get_supabase_client()
        .table(TABLE)
        .insert(
            {
                "state": state,
                "code_verifier": code_verifier,
                "expires_at": expires_at.isoformat(),
            }
        )
        .execute()
    )
    return bool(result.data)


def consume_login_state(state: str) -> dict | None:
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
