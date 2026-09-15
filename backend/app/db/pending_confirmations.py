import json

from postgrest.exceptions import APIError

from app.clients.supabase_client import get_supabase_client


class PendingConfirmationInsertError(Exception):
    pass


def insert_pending_confirmations(
    *,
    conversation_id: str,
    model_message_id: str,
    pending_confirmations: list[dict],
) -> list[dict]:
    if not pending_confirmations:
        return []

    try:
        rows = [
            {
                "function_call_id": confirmation["function_call_id"],
                "llm_name": confirmation["llm_name"],
                "arguments_json": json.loads(confirmation["arguments_json"]),
                "status": "pending",
                "conversation_id": conversation_id,
                "model_message_id": model_message_id,
            }
            for confirmation in pending_confirmations
        ]
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise PendingConfirmationInsertError(
            "La confirmación pendiente tiene datos inválidos"
        ) from exc

    if any(not isinstance(row["arguments_json"], dict) for row in rows):
        raise PendingConfirmationInsertError(
            "Los argumentos de la confirmación deben ser un objeto JSON"
        )

    try:
        result = (
            get_supabase_client()
            .table("pending_confirmations")
            .insert(rows)
            .execute()
        )
    except APIError as exc:
        raise PendingConfirmationInsertError(
            "No se pudieron guardar las confirmaciones pendientes"
        ) from exc

    if not result.data or len(result.data) != len(rows):
        raise PendingConfirmationInsertError(
            "No se pudieron guardar todas las confirmaciones pendientes"
        )

    return result.data
