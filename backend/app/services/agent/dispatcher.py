from app.services.mcp.dispatcher import (
    InvalidToolArgumentsError,
    UnknownCatalogToolError,
)
from app.services.mcp.dispatcher import (
    dispatch_tool_call as dispatch_mcp_tool_call,
)
from app.services.mcp.models import CatalogTool
from app.services.rag import RAG_TOOL_NAME, search_magazines


def _find_catalog_tool(
    catalog: list[CatalogTool],
    llm_name: str,
) -> CatalogTool:
    for tool in catalog:
        if tool.llm_name == llm_name:
            return tool
    raise UnknownCatalogToolError(
        f"No se encontró la tool con llm_name='{llm_name}' en el catálogo"
    )


async def dispatch_tool_call(
    user_id: str,
    catalog: list[CatalogTool],
    llm_name: str,
    arguments: dict,
) -> dict:
    if not isinstance(arguments, dict):
        raise InvalidToolArgumentsError("Los argumentos deben ser un diccionario")

    catalog_tool = _find_catalog_tool(catalog, llm_name)
    if catalog_tool.source == "local":
        if catalog_tool.llm_name != RAG_TOOL_NAME:
            raise UnknownCatalogToolError(
                f"No existe un ejecutor local para '{catalog_tool.llm_name}'"
            )
        try:
            return await search_magazines(arguments)
        except (TypeError, ValueError) as exc:
            raise InvalidToolArgumentsError(str(exc)) from exc

    return await dispatch_mcp_tool_call(
        user_id,
        catalog,
        llm_name,
        arguments,
    )
