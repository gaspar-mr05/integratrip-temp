from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogTool:
    llm_name: str
    description: str
    input_schema_json: str
    server_name: str
    mcp_tool_name: str
