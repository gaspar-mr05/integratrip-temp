import json

from postgrest.exceptions import APIError

from app.clients.supabase_client import get_supabase_client


class PendingConfirmationInsertError(Exception):
    pass


class PendingConfirmationUnavailableError(Exception):
    pass


class PendingConfirmationUpdateError(Exception):
    pass


class PendingConfirmationListError(Exception):
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


def list_pending_confirmations(
    *,
    conversation_id: str,
) -> list[dict]:
    try:
        result = (
            get_supabase_client()
            .table("pending_confirmations")
            .select(
                "id, conversation_id, model_message_id, "
                "function_call_id, llm_name, arguments_json, status"
            )
            .eq("conversation_id", conversation_id)
            .eq("status", "pending")
            .order("created_at", desc=False)
            .execute()
        )
    except APIError as exc:
        raise PendingConfirmationListError(
            "No se pudieron obtener las confirmaciones pendientes"
        ) from exc

    return result.data or []


def _transition_confirmation(
    *,
    conversation_id: str,
    confirmation_id: str,
    expected_status: str,
    target_status: str,
) -> dict:
    try:
        result = (
            get_supabase_client()
            .table("pending_confirmations")
            .update({"status": target_status})
            .eq("id", confirmation_id)
            .eq("conversation_id", conversation_id)
            .eq("status", expected_status)
            .execute()
        )
    except APIError as exc:
        raise PendingConfirmationUpdateError(
            "No se pudo actualizar la confirmación pendiente"
        ) from exc

    if not result.data:
        raise PendingConfirmationUnavailableError(
            "La confirmación pendiente no está disponible para actualizar"
        )

    if len(result.data) != 1:
        raise PendingConfirmationUpdateError(
            "Se actualizaron múltiples confirmaciones pendientes"
        )

    return result.data[0]


def claim_pending_confirmation(
    *,
    conversation_id: str,
    confirmation_id: str,
) -> dict:
    return _transition_confirmation(
        conversation_id=conversation_id,
        confirmation_id=confirmation_id,
        expected_status="pending",
        target_status="processing",
    )


def reject_pending_confirmation(
    *,
    conversation_id: str,
    confirmation_id: str,
) -> dict:
    return _transition_confirmation(
        conversation_id=conversation_id,
        confirmation_id=confirmation_id,
        expected_status="pending",
        target_status="rejected",
    )


def complete_approved_confirmation(
    *,
    conversation_id: str,
    confirmation_id: str,
) -> dict:
    return _transition_confirmation(
        conversation_id=conversation_id,
        confirmation_id=confirmation_id,
        expected_status="processing",
        target_status="approved",
    )
