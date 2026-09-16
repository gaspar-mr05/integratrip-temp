import json

import llm_pb2

from app.db.conversations import touch_conversation
from app.db.messages import insert_messages
from app.db.pending_confirmations import reject_pending_confirmation
from app.services.chat.service import load_conversation_history
from app.services.chat.transform_messages import transform_message_to_dict


class InvalidPendingConfirmationError(Exception):
    pass


def _next_message_sequence(messages: list[dict]) -> int:
    return messages[-1]["sequence"] + 1 if messages else 0


def _build_rejection_message(
    confirmation: dict,
    sequence_number: int,
) -> dict:
    try:
        function_result = llm_pb2.FunctionResult(
            id=confirmation["function_call_id"],
            name=confirmation["llm_name"],
            result_json=json.dumps(
                {"error": "La operación fue rechazada por el usuario"},
                ensure_ascii=False,
            ),
            is_error=True,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPendingConfirmationError(
            "La confirmación pendiente tiene una estructura inválida"
        ) from exc

    tool_message = llm_pb2.Message(
        role=llm_pb2.Message.TOOL,
        function_results=[function_result],
    )
    return transform_message_to_dict(tool_message, sequence_number)


def reject_confirmation(
    user_id: str,
    conversation_id: str,
    confirmation_id: str,
) -> dict:
    _, messages = load_conversation_history(
        user_id=user_id,
        conversation_id=conversation_id,
    )
    confirmation = reject_pending_confirmation(
        conversation_id=conversation_id,
        confirmation_id=confirmation_id,
    )
    message = _build_rejection_message(
        confirmation,
        _next_message_sequence(messages),
    )
    inserted_messages = insert_messages(
        conversation_id=conversation_id,
        messages=[message],
    )
    touch_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )
    return inserted_messages[0]
