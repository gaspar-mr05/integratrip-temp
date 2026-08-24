from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.security.session import get_current_user_id
from app.services.mcp_connection_service import (
    ConnectionFlowError,
    InvalidConnectionStateError,
    McpNotConnectedError,
    McpServerNotFoundError,
    complete_mcp_connection_flow,
    start_mcp_connection_flow,
)
from app.services.mcp_tools_service import McpProtocolError, list_server_tools

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/{server_name}/connect")
def connect_mcp_server(server_name: str, user_id: str = Depends(get_current_user_id)):
    try:
        url = start_mcp_connection_flow(user_id, server_name)
    except McpServerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConnectionFlowError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_description or error)
    if code is None or state is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan los parámetros code y state"
        )

    try:
        complete_mcp_connection_flow(server_name, state, code)
    except McpServerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidConnectionStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ConnectionFlowError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return RedirectResponse(get_settings().FRONTEND_URL)


@router.get("/{server_name}/tools")
async def list_tools(server_name: str, user_id: str = Depends(get_current_user_id)):
    try:
        tools = await list_server_tools(user_id, server_name)
    except McpServerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except McpNotConnectedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (ConnectionFlowError, McpProtocolError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return {"tools": tools}
