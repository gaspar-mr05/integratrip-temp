import json
import re
from dataclasses import dataclass
from app.db.mcp_connections import list_active_mcp_servers
from app.services.mcp_tools_service import list_server_tools

_LLM_TOOL_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}")


class InvalidCatalogToolError(ValueError):
    pass


class DuplicateCatalogToolError(ValueError):
    pass


@dataclass(frozen=True)
class CatalogTool:
    llm_name: str
    description: str
    input_schema_json: str
    server_name: str
    mcp_tool_name: str


def _require_non_empty_string(value: object, error_message: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidCatalogToolError(error_message)
    return value


def _build_llm_name(auth_type: str, mcp_tool_name: str) -> str:
    llm_name = f"{auth_type.lower()}_{mcp_tool_name}"
    if _LLM_TOOL_NAME_PATTERN.fullmatch(llm_name) is None:
        raise InvalidCatalogToolError(
            f"El nombre unificado de la tool no es válido: '{llm_name}'"
        )
    return llm_name


def _get_description(mcp_tool: dict) -> str:
    description = mcp_tool.get("description")
    if description is None:
        return ""
    if not isinstance(description, str):
        raise InvalidCatalogToolError("La descripción de la tool MCP no es válida")
    return description


def _serialize_input_schema(mcp_tool: dict) -> str:
    input_schema = mcp_tool.get("inputSchema")
    if not isinstance(input_schema, dict):
        raise InvalidCatalogToolError("El inputSchema de la tool MCP debe ser un objeto")

    try:
        input_schema_json = json.dumps(input_schema, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise InvalidCatalogToolError(
            "El inputSchema de la tool MCP no es serializable como JSON"
        ) from exc
    return input_schema_json


def _build_catalog_tool(mcp_server: dict, mcp_tool: dict) -> CatalogTool:
    server_name = _require_non_empty_string(
        mcp_server.get("name"),
        "El servidor MCP no tiene un nombre válido",
    )
    auth_type = _require_non_empty_string(
        mcp_server.get("auth_type"),
        "El servidor MCP no tiene un auth_type válido",
    )
    mcp_tool_name = _require_non_empty_string(
        mcp_tool.get("name"),
        "La tool MCP no tiene un nombre válido",
    )

    return CatalogTool(
        llm_name=_build_llm_name(auth_type, mcp_tool_name),
        description=_get_description(mcp_tool),
        input_schema_json=_serialize_input_schema(mcp_tool),
        server_name=server_name,
        mcp_tool_name=mcp_tool_name,
    )


async def build_tool_catalog(user_id: str) -> list[CatalogTool]:
    catalog_tools: list[CatalogTool] = []
    used_names: set[str] = set()

    for mcp_server in list_active_mcp_servers(user_id):
        server_name = _require_non_empty_string(
            mcp_server.get("name"),
            "El servidor MCP no tiene un nombre válido",
        )
        mcp_tools = await list_server_tools(user_id, server_name)

        for mcp_tool in mcp_tools:
            catalog_tool = _build_catalog_tool(mcp_server, mcp_tool)
            if catalog_tool.llm_name in used_names:
                raise DuplicateCatalogToolError(
                    f"Se encontró una tool duplicada con llm_name='{catalog_tool.llm_name}'"
                )

            used_names.add(catalog_tool.llm_name)
            catalog_tools.append(catalog_tool)

    return catalog_tools
