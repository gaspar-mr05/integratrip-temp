from app.services.mcp.models import CatalogTool
from app.services.mcp.tools import call_server_tool


class UnknownCatalogToolError(ValueError):
    pass


class InvalidToolArgumentsError(ValueError):
    pass


def _find_catalog_tool(catalog: list[CatalogTool], llm_name: str) -> CatalogTool:
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
        argument_type = type(arguments).__name__
        raise InvalidToolArgumentsError(
            f"Los argumentos deben ser un diccionario, se recibió: {argument_type}"
        )

    catalog_tool = _find_catalog_tool(catalog, llm_name)
    return await call_server_tool(
        user_id,
        catalog_tool.server_name,
        catalog_tool.mcp_tool_name,
        arguments,
    )
