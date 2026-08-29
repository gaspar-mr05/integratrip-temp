

import logging

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client

from app.services.mcp_connection_service import (
    get_valid_access_token,
    mcp_endpoint,
    resolve_mcp_server,
)

logger = logging.getLogger(__name__)


class McpProtocolError(Exception):
    pass


async def _log_http_errors(response) -> None:
    if response.status_code < 400:
        return

    await response.aread()
    logger.error(
        "El servidor MCP respondió %s en %s: %s | www-authenticate=%s",
        response.status_code,
        response.request.url,
        response.text[:500],
        response.headers.get("www-authenticate"),
    )


async def _fetch_tools(endpoint: str, access_token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {access_token}"}

    async with create_mcp_http_client(headers=headers) as http_client:
        http_client.event_hooks["response"].append(_log_http_errors)

        async with streamable_http_client(endpoint, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.model_dump() for tool in result.tools]


async def list_server_tools(user_id: str, server_name: str) -> list[dict]:
    mcp_server = resolve_mcp_server(server_name)
    access_token = get_valid_access_token(user_id, mcp_server)

    try:
        return await _fetch_tools(mcp_endpoint(mcp_server), access_token)
    except Exception as exc:
        logger.exception("Error consultando las tools de '%s'", server_name)
        raise McpProtocolError(f"Error consultando las tools de '{server_name}'") from exc



async def _call_tool(
    endpoint: str,
    access_token: str,
    tool_name: str,
    params: dict,
) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}

    async with create_mcp_http_client(headers=headers) as http_client:
        http_client.event_hooks["response"].append(_log_http_errors)

        async with streamable_http_client(endpoint, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                return result.model_dump()


async def call_server_tool(
    user_id: str,
    server_name: str,
    tool_name: str,
    params: dict,
) -> dict:
    mcp_server = resolve_mcp_server(server_name)
    access_token = get_valid_access_token(user_id, mcp_server)

    try:
        return await _call_tool(
            mcp_endpoint(mcp_server),
            access_token,
            tool_name,
            params,
        )
    except Exception as exc:
        logger.exception(
            "Error llamando a la tool '%s' en '%s'",
            tool_name,
            server_name,
        )
        raise McpProtocolError(
            f"Error llamando a la tool '{tool_name}' en '{server_name}'"
        ) from exc