from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.security.session import get_current_user_id
from app.services.mcp_connection_service import (
    ConnectionFlowError,
    InvalidConnectionStateError,
    start_mcp_connection_flow,
    complete_mcp_connection_flow,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/{server_name}/connect")
def connect_mcp_server(server_name: str, user_id: str = Depends(get_current_user_id)):
    try:
        url = start_mcp_connection_flow(user_id, server_name)
    except ConnectionFlowError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return RedirectResponse(url)


@router.get("/{server_name}/callback")
def mcp_callback(
    server_name: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    if error is not None:
        raise HTTPException(status_code=400, detail=error_description or error)
    if code is None or state is None:
        raise HTTPException(status_code=400, detail="Faltan los parámetros code y state")

    try:
        complete_mcp_connection_flow(server_name, state, code)
    except InvalidConnectionStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConnectionFlowError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    settings = get_settings()
    return RedirectResponse(settings.FRONTEND_URL)