import llm_pb2

from app.db.conversations import get_conversation, touch_conversation
from app.db.messages import insert_messages, list_messages
from app.db.pending_confirmations import insert_pending_confirmations
from app.services.agent import (
    AgentRunResult,
    PendingToolConfirmation,
    resume_agent,
    run_agent,
)
from app.services.chat.transform_messages import (
    transform_dict_to_message,
    transform_message_to_dict,
)


class EmptyUserTextError(Exception):
    pass


class ConversationNotFoundError(Exception):
    pass


class PendingConfirmationMessageNotFoundError(Exception):
    pass


def load_conversation_history(
    user_id: str,
    conversation_id: str,
) -> tuple[dict, list[dict]]:
    conversation = get_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )
    if not conversation:
        raise ConversationNotFoundError(
            "La conversación no existe o no pertenece al usuario"
        )

    messages = list_messages(conversation_id=conversation_id)
    return conversation, messages


def _validate_user_text(user_text: str) -> None:
    if not user_text.strip():
        raise EmptyUserTextError("El texto del usuario no puede estar vacío")


def _load_history(
    user_id: str,
    conversation_id: str,
) -> tuple[list[dict], list[llm_pb2.Message]]:
    _, rows = load_conversation_history(
        user_id,
        conversation_id,
    )
    history = [transform_dict_to_message(row) for row in rows]
    return rows, history


def _build_generated_rows(
    stored_rows: list[dict],
    result: AgentRunResult,
) -> list[dict]:
    first_sequence = stored_rows[-1]["sequence"] + 1 if stored_rows else 0
    return [
        transform_message_to_dict(message, first_sequence + offset)
        for offset, message in enumerate(result.generated_messages)
    ]


def _find_pending_model_message_id(
    inserted_messages: list[dict],
    pending_confirmations: tuple[PendingToolConfirmation, ...],
) -> str:
    pending_call_ids = {
        confirmation.function_call_id
        for confirmation in pending_confirmations
    }
    matching_message_ids = []

    for message in inserted_messages:
        if message.get("role") != "model":
            continue

        function_calls = message.get("function_calls")
        if not isinstance(function_calls, list):
            continue

        message_call_ids = {
            function_call.get("id")
            for function_call in function_calls
            if isinstance(function_call, dict)
        }
        message_id = message.get("id")
        if (
            pending_call_ids.issubset(message_call_ids)
            and isinstance(message_id, str)
            and message_id
        ):
            matching_message_ids.append(message_id)

    if len(matching_message_ids) != 1:
        raise PendingConfirmationMessageNotFoundError(
            "No se encontró el mensaje que originó las confirmaciones pendientes"
        )

    return matching_message_ids[0]


def _persist_pending_confirmations(
    conversation_id: str,
    inserted_messages: list[dict],
    pending_confirmations: tuple[PendingToolConfirmation, ...],
) -> None:
    if not pending_confirmations:
        return

    model_message_id = _find_pending_model_message_id(
        inserted_messages,
        pending_confirmations,
    )
    confirmation_rows = [
        {
            "function_call_id": confirmation.function_call_id,
            "llm_name": confirmation.llm_name,
            "arguments_json": confirmation.arguments_json,
        }
        for confirmation in pending_confirmations
    ]
    insert_pending_confirmations(
        conversation_id=conversation_id,
        model_message_id=model_message_id,
        pending_confirmations=confirmation_rows,
    )


def _persist_agent_result(
    user_id: str,
    conversation_id: str,
    stored_rows: list[dict],
    result: AgentRunResult,
) -> None:
    generated_rows = _build_generated_rows(stored_rows, result)
    inserted_messages = insert_messages(
        conversation_id=conversation_id,
        messages=generated_rows,
    )
    _persist_pending_confirmations(
        conversation_id,
        inserted_messages,
        result.pending_confirmations,
    )
    touch_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )


async def run_conversation_turn(
    user_id: str,
    conversation_id: str,
    user_text: str,
) -> AgentRunResult:
    _validate_user_text(user_text)
    stored_rows, history = _load_history(user_id, conversation_id)
    result = await run_agent(user_id, history, user_text)

    _persist_agent_result(
        user_id,
        conversation_id,
        stored_rows,
        result,
    )

    return result



async def resume_conversation(
    user_id: str,
    conversation_id: str,
) -> AgentRunResult:
    stored_rows, history = _load_history(
        user_id,
        conversation_id,
    )
    result = await resume_agent(user_id, history)

    _persist_agent_result(
        user_id,
        conversation_id,
        stored_rows,
        result,
    )

    return result
