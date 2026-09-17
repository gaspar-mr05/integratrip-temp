from fastapi import APIRouter, Depends, HTTPException, status

from app.clients.llm_client import LlmRateLimitError
from app.db.conversations import (
    create_conversation,
    list_conversations,
    update_conversation_title,
)
from app.db.pending_confirmations import (
    PendingConfirmationUnavailableError,
    list_pending_confirmations,
)
from app.schemas.conversations import SendMessageRequest
from app.security.session import get_current_user_id
from app.services.agent import AgentTurnLimitError
from app.services.chat import (
    ConversationNotFoundError,
    EmptyUserTextError,
    approve_confirmation,
    load_conversation_history,
    reject_confirmation,
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
    return create_conversation(user_id=user_id)


@router.get("", status_code=status.HTTP_200_OK)
def list_conversations_endpoint(
    user_id: str = Depends(get_current_user_id),
):
    return list_conversations(user_id=user_id)


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
        pending_confirmations = list_pending_confirmations(
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La conversación no existe o no pertenece al usuario",
        ) from exc
    return {
        "conversation": conversation,
        "messages": messages,
        "pending_confirmations": pending_confirmations,
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
    return result


@router.post(
    "/{conversation_id}/confirmations/{confirmation_id}/approve",
    status_code=status.HTTP_200_OK,
)
async def approve_confirmation_endpoint(
    conversation_id: str,
    confirmation_id: str,
    user_id: str = Depends(get_current_user_id),
):
    try:
        result = await approve_confirmation(
            user_id=user_id,
            conversation_id=conversation_id,
            confirmation_id=confirmation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La conversación no existe o no pertenece al usuario",
        ) from exc
    except PendingConfirmationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La confirmación ya fue procesada o no está disponible",
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
    return result


@router.post(
    "/{conversation_id}/confirmations/{confirmation_id}/reject",
    status_code=status.HTTP_200_OK,
)
async def reject_confirmation_endpoint(
    conversation_id: str,
    confirmation_id: str,
    user_id: str = Depends(get_current_user_id),
):
    try:
        result = await reject_confirmation(
            user_id=user_id,
            conversation_id=conversation_id,
            confirmation_id=confirmation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La conversación no existe o no pertenece al usuario",
        ) from exc
    except PendingConfirmationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La confirmación ya fue procesada o no está disponible",
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
    return result


