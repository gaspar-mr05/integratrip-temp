from fastapi import APIRouter, Depends, HTTPException, status

from app.clients.llm_client import LlmRateLimitError
from app.db.conversations import (
    ConversationCreateError,
    ConversationListError,
    ConversationReadError,
    ConversationUpdateError,
    create_conversation,
    list_conversations,
)
from app.db.messages import MessageInsertError, MessageListError
from app.db.pending_confirmations import PendingConfirmationInsertError
from app.schemas.conversations import SendMessageRequest
from app.security.session import get_current_user_id
from app.services.agent import AgentTurnLimitError
from app.services.chat import (
    ConversationNotFoundError,
    EmptyUserTextError,
    InvalidStoredMessageError,
    PendingConfirmationMessageNotFoundError,
    load_conversation_history,
    run_conversation_turn,
)


router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation_endpoint(
    user_id: str = Depends(get_current_user_id),
):
    try:
        return create_conversation(user_id=user_id)
    except ConversationCreateError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo crear la conversación",
        ) from exc


@router.get("", status_code=status.HTTP_200_OK)
def list_conversations_endpoint(
    user_id: str = Depends(get_current_user_id),
):
    try:
        return list_conversations(user_id=user_id)
    except ConversationListError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo listar las conversaciones",
        ) from exc


@router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
def get_conversation_endpoint(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
):
    try:
        conversation, messages = load_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La conversación no existe o no pertenece al usuario",
        ) from exc
    except (ConversationReadError, MessageListError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo obtener la conversación",
        ) from exc

    return {
        "conversation": conversation,
        "messages": messages,
    }


@router.post("/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_message_endpoint(
    conversation_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        result = await run_conversation_turn(
            user_id=user_id,
            conversation_id=conversation_id,
            user_text=request.text,
        )
    except EmptyUserTextError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El texto del usuario no puede estar vacío",
        ) from exc
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La conversación no existe o no pertenece al usuario",
        ) from exc
    except LlmRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se alcanzó el límite de solicitudes al servicio LLM",
        ) from exc
    except AgentTurnLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El agente no pudo completar la respuesta",
        ) from exc
    except (
        ConversationReadError,
        ConversationUpdateError,
        InvalidStoredMessageError,
        MessageInsertError,
        MessageListError,
        PendingConfirmationInsertError,
        PendingConfirmationMessageNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo procesar el mensaje",
        ) from exc

    return {
        "text": result.generated_messages[-1].text,
        "pending_confirmations": [
            {
                "function_call_id": confirmation.function_call_id,
                "llm_name": confirmation.llm_name,
                "arguments_json": confirmation.arguments_json,
            }
            for confirmation in result.pending_confirmations
        ],
    }


@router.post("/{conversation_id}/messages/{message_id}/approve", status_code=status.HTTP_201_CREATED)
def approve_message_endpoint(
    conversation_id: str,
    message_id: str,
    user_id: str = Depends(get_current_user_id),
):
    pass

@router.post("/{conversation_id}/messages/{message_id}/reject", status_code=status.HTTP_201_CREATED)
def reject_message_endpoint(
    conversation_id: str,
    message_id: str,
    user_id: str = Depends(get_current_user_id),
):
    pass

