import llm_pb2

from app.clients.llm_client import LlmClient
from app.services.agent.models import AgentRunResult
from app.services.agent.tool_calls import build_tool_exchange, find_pending_confirmations
from app.services.mcp.catalog import build_tool_catalog
from app.services.mcp.models import CatalogTool

MAX_AGENT_TURNS = 12


class InvalidAgentResponseError(Exception):
    pass


class AgentTurnLimitError(Exception):
    pass


def _build_llm_tools(catalog: list[CatalogTool]) -> list[llm_pb2.Tool]:
    return [
        llm_pb2.Tool(
            name=tool.llm_name,
            description=tool.description,
            input_schema_json=tool.input_schema_json,
        )
        for tool in catalog
    ]


async def _generate_turn(
    client: LlmClient,
    messages: list[llm_pb2.Message],
    llm_tools: list[llm_pb2.Tool],
) -> llm_pb2.GenerateResponse:
    request = llm_pb2.GenerateRequest(
        messages=messages,
        tools=llm_tools,
    )
    return await client.generate(request)


def _validate_agent_response(response: llm_pb2.GenerateResponse) -> None:
    if response.stop and response.function_calls:
        raise InvalidAgentResponseError(
            "El LLM indicó detenerse y ejecutar tools al mismo tiempo"
        )

    if not response.stop and not response.function_calls:
        raise InvalidAgentResponseError(
            "El LLM no entregó una respuesta final ni solicitó tools"
        )


async def run_agent(
    user_id: str,
    history: list[llm_pb2.Message],
    user_text: str,
) -> AgentRunResult:
    catalog = await build_tool_catalog(user_id)
    llm_tools = _build_llm_tools(catalog)
    user_message = llm_pb2.Message(
        role=llm_pb2.Message.USER,
        text=user_text,
    )
    messages = [*history, user_message]
    generated_messages = [user_message]

    async with LlmClient() as client:
        for turn_index in range(MAX_AGENT_TURNS):
            response = await _generate_turn(client, messages, llm_tools)
            _validate_agent_response(response)

            if response.stop:
                final_message = llm_pb2.Message(
                    role=llm_pb2.Message.MODEL,
                    text=response.text,
                )
                generated_messages.append(final_message)

                return AgentRunResult(
                    final_response=response,
                    generated_messages=tuple(generated_messages),
                )

            pending_confirmations = find_pending_confirmations(
                catalog,
                response.function_calls,
            )
            if pending_confirmations:
                model_message = llm_pb2.Message(
                    role=llm_pb2.Message.MODEL,
                    text=response.text,
                    function_calls=response.function_calls,
                )
                generated_messages.append(model_message)

                return AgentRunResult(
                    final_response=None,
                    generated_messages=tuple(generated_messages),
                    pending_confirmations=pending_confirmations,
                )

            if turn_index == MAX_AGENT_TURNS - 1:
                break

            tool_exchange = await build_tool_exchange(user_id, catalog, response)
            messages.extend(tool_exchange)
            generated_messages.extend(tool_exchange)

    raise AgentTurnLimitError(
        f"El agente alcanzó el límite de {MAX_AGENT_TURNS} turnos"
    )
