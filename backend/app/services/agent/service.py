import json
import re
from uuid import uuid4

import llm_pb2
from app.clients.llm_client import LlmClient
from app.services.agent.models import AgentRunResult, PendingToolConfirmation
from app.services.agent.tool_calls import (
    CONFIRMATION_REQUIRED_MCP_TOOLS,
    build_tool_exchange,
    find_pending_confirmations,
)
from app.services.mcp.catalog import build_tool_catalog
from app.services.mcp.models import CatalogTool
from app.services.rag.catalog import RAG_TOOL_NAME, REJECTION_SENTENCE

MAX_AGENT_TURNS = 12


class InvalidAgentResponseError(Exception):
    pass


class AgentTurnLimitError(Exception):
    pass


class InvalidAgentResumeError(Exception):
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
    response = await client.generate(request)

    for function_call in response.function_calls:
        if not function_call.id.strip():
            function_call.id = str(uuid4())

    return response


def _validate_agent_response(response: llm_pb2.GenerateResponse) -> None:
    if response.stop and response.function_calls:
        raise InvalidAgentResponseError(
            "El LLM indicó detenerse y ejecutar tools al mismo tiempo"
        )

    if not response.stop and not response.function_calls:
        raise InvalidAgentResponseError(
            "El LLM no entregó una respuesta final ni solicitó tools"
        )


def _validate_resume_history(history: list[llm_pb2.Message]) -> None:
    if not history:
        raise InvalidAgentResumeError(
            "No se puede reanudar un agente sin historial"
        )

    if history[-1].role != llm_pb2.Message.TOOL:
        raise InvalidAgentResumeError(
            "El último mensaje debe contener un resultado de tool"
        )


def _build_final_result(
    response: llm_pb2.GenerateResponse,
    messages: list[llm_pb2.Message],
    generated_messages: list[llm_pb2.Message],
) -> AgentRunResult:
    response.text = _enforce_rag_rejection(response.text, messages)
    final_message = llm_pb2.Message(
        role=llm_pb2.Message.MODEL,
        text=response.text,
    )
    generated_messages.append(final_message)

    return AgentRunResult(
        final_response=response,
        generated_messages=tuple(generated_messages),
    )


def _current_turn_messages(
    messages: list[llm_pb2.Message],
) -> list[llm_pb2.Message]:
    for index in range(len(messages) - 1, -1, -1):
        if messages[index].role == llm_pb2.Message.USER:
            return messages[index + 1 :]
    return []


def _current_turn_tool_names(
    messages: list[llm_pb2.Message],
) -> set[str]:
    tool_names: set[str] = set()
    for message in _current_turn_messages(messages):
        tool_names.update(call.name for call in message.function_calls)
        tool_names.update(result.name for result in message.function_results)
    return tool_names


def _build_contextual_llm_tools(
    catalog: list[CatalogTool],
    messages: list[llm_pb2.Message],
) -> list[llm_pb2.Tool]:
    used_tool_names = _current_turn_tool_names(messages)
    if not used_tool_names:
        return _build_llm_tools(catalog)

    used_server_names = {
        tool.server_name
        for tool in catalog
        if tool.llm_name in used_tool_names and tool.server_name is not None
    }
    contextual_catalog = [
        tool
        for tool in catalog
        if tool.llm_name in used_tool_names
        or (
            tool.server_name in used_server_names
            and tool.mcp_tool_name in CONFIRMATION_REQUIRED_MCP_TOOLS
        )
    ]
    if not contextual_catalog:
        return _build_llm_tools(catalog)
    return _build_llm_tools(contextual_catalog)


def _current_rag_response_mode(
    messages: list[llm_pb2.Message],
) -> str | None:
    response_mode = None
    for message in _current_turn_messages(messages):
        for function_result in message.function_results:
            if function_result.name != RAG_TOOL_NAME or function_result.is_error:
                continue
            try:
                payload = json.loads(function_result.result_json)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and isinstance(
                payload.get("response_mode"), str
            ):
                response_mode = payload["response_mode"]
    return response_mode


def _enforce_rag_rejection(
    response_text: str,
    messages: list[llm_pb2.Message],
) -> str:
    if (
        _current_rag_response_mode(messages) != "reject"
        or REJECTION_SENTENCE in response_text
    ):
        return response_text

    sentences = re.split(r"(?<=[.!?])\s+|\n+", response_text.strip())
    preserved = [
        sentence
        for sentence in sentences
        if sentence and "revista" not in sentence.casefold()
    ]
    preserved.append(REJECTION_SENTENCE)
    return "\n".join(preserved)


def _build_pending_result(
    generated_messages: list[llm_pb2.Message],
    pending_confirmations: tuple[PendingToolConfirmation, ...],
) -> AgentRunResult:
    return AgentRunResult(
        final_response=None,
        generated_messages=tuple(generated_messages),
        pending_confirmations=pending_confirmations,
    )


async def _run_agent_loop(
    user_id: str,
    messages: list[llm_pb2.Message],
    generated_messages: list[llm_pb2.Message],
) -> AgentRunResult:
    catalog = await build_tool_catalog(user_id)
    llm_tools = _build_contextual_llm_tools(catalog, messages)

    async with LlmClient() as client:
        for turn_index in range(MAX_AGENT_TURNS):
            response = await _generate_turn(client, messages, llm_tools)
            _validate_agent_response(response)

            if response.stop:
                return _build_final_result(
                    response,
                    messages,
                    generated_messages,
                )

            pending_confirmations = find_pending_confirmations(
                catalog,
                response.function_calls,
            )
            if pending_confirmations:
                deferred_call_ids = frozenset(
                    confirmation.function_call_id
                    for confirmation in pending_confirmations
                )
                tool_exchange = await build_tool_exchange(
                    user_id,
                    catalog,
                    response,
                    deferred_call_ids=deferred_call_ids,
                )
                generated_messages.extend(tool_exchange)
                return _build_pending_result(
                    generated_messages,
                    pending_confirmations,
                )

            if turn_index == MAX_AGENT_TURNS - 1:
                break

            tool_exchange = await build_tool_exchange(
                user_id,
                catalog,
                response,
            )
            messages.extend(tool_exchange)
            generated_messages.extend(tool_exchange)
            llm_tools = _build_contextual_llm_tools(catalog, messages)

    raise AgentTurnLimitError(
        f"El agente alcanzó el límite de {MAX_AGENT_TURNS} turnos"
    )


async def run_agent(
    user_id: str,
    history: list[llm_pb2.Message],
    user_text: str,
) -> AgentRunResult:
    user_message = llm_pb2.Message(
        role=llm_pb2.Message.USER,
        text=user_text,
    )
    messages = [*history, user_message]
    generated_messages = [user_message]

    return await _run_agent_loop(
        user_id,
        messages,
        generated_messages,
    )


async def resume_agent(
    user_id: str,
    history: list[llm_pb2.Message],
) -> AgentRunResult:
    _validate_resume_history(history)

    return await _run_agent_loop(
        user_id,
        [*history],
        [],
    )
