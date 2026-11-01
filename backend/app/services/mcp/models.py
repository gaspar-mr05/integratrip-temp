from dataclasses import dataclass
from typing import Literal

ToolSource = Literal["mcp", "local"]


@dataclass(frozen=True)
class CatalogTool:
    llm_name: str
    description: str
    input_schema_json: str
    server_name: str | None = None
    mcp_tool_name: str | None = None
    source: ToolSource = "mcp"
