from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db.mcp_servers import get_mcp_server_by_name
from app.services.oauth.cimd import build_client_metadata

router = APIRouter(tags=["oauth"])

CIMD_SERVER_NAME = "cielo-sur"
CLIENT_METADATA_PATH = "/.well-known/oauth-client-metadata.json"


@router.get(CLIENT_METADATA_PATH)
def oauth_client_metadata():
    mcp_server = get_mcp_server_by_name(CIMD_SERVER_NAME)
    if mcp_server is None:
        raise HTTPException(
            status_code=500, detail=f"No existe el servidor MCP '{CIMD_SERVER_NAME}'"
        )


    metadata_base_url = (
        get_settings().BACKEND_URL
        if get_settings().ENVIRONMENT == "local"
        else f"{get_settings().FRONTEND_URL}/api"
    )

    return build_client_metadata(
        metadata_url=f"{metadata_base_url}{CLIENT_METADATA_PATH}",
        redirect_uris=mcp_server["redirect_uris"],
    )
