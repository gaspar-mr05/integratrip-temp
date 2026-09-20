import llm_pb2

from app.db.conversations import (
    DEFAULT_CONVERSATION_TITLE,
    get_conversation,
    touch_conversation,
    update_conversation_title,
)
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


MAX_CONVERSATION_TITLE_LENGTH = 60


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


def _build_conversation_title(user_text: str) -> str:
    normalized_text = " ".join(user_text.split())
    if len(normalized_text) <= MAX_CONVERSATION_TITLE_LENGTH:
        return normalized_text

    return f"{normalized_text[: MAX_CONVERSATION_TITLE_LENGTH - 1].rstrip()}…"


def _load_history(
    user_id: str,
    conversation_id: str,
) -> tuple[dict, list[dict], list[llm_pb2.Message]]:
    conversation, rows = load_conversation_history(
        user_id,
        conversation_id,
    )
    history = [transform_dict_to_message(row) for row in rows]
    return conversation, rows, history


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
) -> list[dict]:
    if not pending_confirmations:
        return []

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

    return insert_pending_confirmations(
        conversation_id=conversation_id,
        model_message_id=model_message_id,
        pending_confirmations=confirmation_rows,
    )


def _persist_agent_result(
    user_id: str,
    conversation_id: str,
    stored_rows: list[dict],
    result: AgentRunResult,
) -> list[dict]:
    generated_rows = _build_generated_rows(stored_rows, result)
    inserted_messages = insert_messages(
        conversation_id=conversation_id,
        messages=generated_rows,
    )
    inserted_confirmations = _persist_pending_confirmations(
        conversation_id,
        inserted_messages,
        result.pending_confirmations,
    )

    touch_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    return inserted_confirmations


async def run_conversation_turn(
    user_id: str,
    conversation_id: str,
    user_text: str,
) -> dict:
    _validate_user_text(user_text)
    conversation, stored_rows, history = _load_history(user_id, conversation_id)
    agent_result = await run_agent(user_id, history, user_text)

    inserted_confirmations = _persist_agent_result(
        user_id,
        conversation_id,
        stored_rows,
        agent_result,
    )

    if (
        not stored_rows
        and conversation.get("title") == DEFAULT_CONVERSATION_TITLE
    ):
        update_conversation_title(
            user_id=user_id,
            conversation_id=conversation_id,
            title=_build_conversation_title(user_text),
        )

    return {
        "text": agent_result.generated_messages[-1].text,
        "pending_confirmations": inserted_confirmations,
    }


async def resume_conversation(
    user_id: str,
    conversation_id: str,
) -> dict:
    _, stored_rows, history = _load_history(
        user_id,
        conversation_id,
    )
    agent_result = await resume_agent(user_id, history)

    inserted_confirmations = _persist_agent_result(
        user_id,
        conversation_id,
        stored_rows,
        agent_result,
    )

    return {
        "text": agent_result.generated_messages[-1].text,
        "pending_confirmations": inserted_confirmations,
    }
