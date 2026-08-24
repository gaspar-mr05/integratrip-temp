import logging

from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def get_mcp_server_by_name(name: str) -> dict | None:
    supabase = get_supabase_client()
    result = supabase.table("mcp_servers").select("*").eq("name", name).execute()
    return result.data[0] if result.data else None


def update_mcp_server_credentials(
    server_id: str, client_id: str, client_secret: str | None
) -> dict | None:
    supabase = get_supabase_client()
    try:
        result = (
            supabase.table("mcp_servers")
            .update({"client_id": client_id, "client_secret_enc": client_secret})
            .eq("id", server_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        logger.exception("Error actualizando credenciales del mcp_server_id=%s", server_id)
        return None
