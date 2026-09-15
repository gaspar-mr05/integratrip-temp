from postgrest.exceptions import APIError

from app.clients.supabase_client import get_supabase_client


class MessageInsertError(Exception):
    pass

class MessageListError(Exception):
    pass

def insert_messages(
    *,
    conversation_id: str,
    messages: list[dict],
) -> list[dict]:
    if not messages:
        return []

    rows = [
        {
            **message,
            "conversation_id": conversation_id,
        }
        for message in messages
    ]

    try:
        result = (
            get_supabase_client()
            .table("messages")
            .insert(rows)
            .execute()
        )
    except APIError as exc:
        raise MessageInsertError(
            "No se pudieron guardar los mensajes"
        ) from exc

    if not result.data or len(result.data) != len(rows):
        raise MessageInsertError(
            "No se pudieron guardar todos los mensajes"
        )

    return result.data

def list_messages(*, conversation_id: str) -> list[dict]:
    try:
        result = (
            get_supabase_client()
            .table("messages")
            .select("id, conversation_id, sequence, role, text, function_calls, function_results, created_at")
            .eq("conversation_id", conversation_id)
            .order("sequence", desc=False)
            .execute()
        )
    except APIError as exc:
        raise MessageListError(
            "No se pudieron obtener los mensajes"
        ) from exc

    if not result.data:
        return []

    return result.data