"""Prueba manual del listado de tools.

Uso: python -m scripts.list_mcp_tools <user_id> [server_name]
"""

import asyncio
import sys

from app.services.mcp_connection_service import (
    ConnectionFlowError,
    McpNotConnectedError,
    McpServerNotFoundError,
)
from app.services.mcp_tools_service import McpProtocolError, list_server_tools

DEFAULT_SERVER_NAME = "andes-air"


async def main(user_id: str, server_name: str) -> None:
    try:
        tools = await list_server_tools(user_id, server_name)
    except (
        McpServerNotFoundError,
        McpNotConnectedError,
        ConnectionFlowError,
        McpProtocolError,
    ) as exc:
        print(f"{type(exc).__name__}: {exc}")
        return

    print(f"{len(tools)} tools en '{server_name}':")
    for tool in tools:
        print("---")
        print(tool)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    server = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SERVER_NAME
    asyncio.run(main(sys.argv[1], server))
