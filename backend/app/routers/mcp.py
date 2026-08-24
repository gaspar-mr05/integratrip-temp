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

from app.db.mcp_connections import get_mcp_connection
from app.db.mcp_servers import get_mcp_server_by_name

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


@router.get("/{server_name}/tools")
def list_tools(server_name: str, user_id: str = Depends(get_current_user_id)):
    mcp_server = get_mcp_server_by_name(server_name)
    if mcp_server is None:
        raise HTTPException(status_code=404, detail=f"No existe el servidor MCP '{server_name}'")

    mcp_connection = get_mcp_connection(user_id, mcp_server["id"])
    if mcp_connection is None:
        raise HTTPException(status_code=404, detail=f"No has conectado '{server_name}' todavía")

    access_token = mcp_connection["access_token_enc"]
