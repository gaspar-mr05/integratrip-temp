from datetime import datetime, timezone

from postgrest.exceptions import APIError

from app.clients.supabase_client import get_supabase_client

DEFAULT_CONVERSATION_TITLE = "Nueva conversación"


class ConversationCreateError(Exception):
    pass


class ConversationListError(Exception):
    pass


class ConversationReadError(Exception):
    pass


class ConversationUpdateError(Exception):
    pass


def create_conversation(
    *,
    user_id: str,
    title: str = DEFAULT_CONVERSATION_TITLE,
) -> dict:
    try:
        result = (
            get_supabase_client()
            .table("conversations")
            .insert(
                {
                    "user_id": user_id,
                    "title": title,
                }
            )
            .execute()
        )
    except APIError as exc:
        raise ConversationCreateError(
            "No se pudo crear la conversación"
        ) from exc

    if not result.data:
        raise ConversationCreateError(
            "No se pudo crear la conversación"
        )

    return result.data[0]


def list_conversations(*, user_id: str) -> list[dict]:
    try:
        result = (
            get_supabase_client()
            .table("conversations")
            .select("id,title,created_at,updated_at")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
    except APIError as exc:
        raise ConversationListError(
            "No se pudieron obtener las conversaciones"
        ) from exc

    return result.data or []

def get_conversation(
    *,
    user_id: str,
    conversation_id: str,
) -> dict | None:
    try:
        result = (
            get_supabase_client()
            .table("conversations")
            .select("id,user_id,title,created_at,updated_at")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    except APIError as exc:
        raise ConversationReadError(
            "No se pudo obtener la conversación"
        ) from exc

    return result.data[0] if result.data else None


def touch_conversation(*, user_id: str, conversation_id: str) -> dict:
    updated_at = datetime.now(timezone.utc).isoformat()
    try:
        result = (
            get_supabase_client()
            .table("conversations")
            .update({"updated_at": updated_at})
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
    except APIError as exc:
        raise ConversationUpdateError(
            "No se pudo actualizar la conversación"
        ) from exc

    if not result.data or len(result.data) != 1:
        raise ConversationUpdateError(
            "No se pudo actualizar la conversación"
        )

    return result.data[0]


def update_conversation_title(
    *,
    user_id: str,
    conversation_id: str,
    title: str,
) -> dict:
    try:
        result = (
            get_supabase_client()
            .table("conversations")
            .update({"title": title})
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
    except APIError as exc:
        raise ConversationUpdateError(
            "No se pudo actualizar la conversación"
        ) from exc

    if not result.data or len(result.data) != 1:
        raise ConversationUpdateError(
            "No se pudo actualizar la conversación"
        )

    return result.data[0]
