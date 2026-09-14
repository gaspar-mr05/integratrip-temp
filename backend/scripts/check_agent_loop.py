import asyncio
import sys
from unittest.mock import patch

import llm_pb2

from app.services.agent import run_agent
from app.services.mcp.catalog import build_tool_catalog
from app.services.mcp.models import CatalogTool

SAFE_TOOL_NAMES = {
    "cimd_get_current_weather",
    "cimd_get_forecast",
    "cimd_get_weather_alerts",
    "cimd_list_cities",
}
USAGE = "Uso: python -m scripts.check_agent_loop <user_id>"


async def _build_safe_catalog(user_id: str) -> list[CatalogTool]:
    catalog = await build_tool_catalog(user_id)
    return [tool for tool in catalog if tool.llm_name in SAFE_TOOL_NAMES]


def _print_trace(messages: tuple[llm_pb2.Message, ...]) -> None:
    role_names = {
        llm_pb2.Message.USER: "USER",
        llm_pb2.Message.MODEL: "MODEL",
        llm_pb2.Message.TOOL: "TOOL",
    }

    print("\nSecuencia generada:")
    for message in messages:
        print(f"- {role_names.get(message.role, 'UNKNOWN')}")
        for function_call in message.function_calls:
            print(f"  llamada: {function_call.name}")
        for function_result in message.function_results:
            status = "ERROR" if function_result.is_error else "OK"
            print(f"  resultado: {function_result.name} [{status}]")


async def main(user_id: str) -> None:
    with patch(
        "app.services.agent.service.build_tool_catalog",
        new=_build_safe_catalog,
    ):
        result = await run_agent(
            user_id=user_id,
            history=[],
            user_text=(
                "Dime el clima actual de Santiago de Chile. "
                "Solo consulta información: no reserves ni canceles nada."
            ),
        )

    print("\nRespuesta final:")
    print(result.final_response.text)
    _print_trace(result.generated_messages)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
