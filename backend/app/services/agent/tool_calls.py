import json
from collections.abc import Iterable

import llm_pb2
from app.services.agent.dispatcher import (
    InvalidToolArgumentsError,
    UnknownCatalogToolError,
    dispatch_tool_call,
)
from app.services.agent.models import PendingToolConfirmation
from app.services.mcp.catalog import build_tool_catalog
from app.services.mcp.models import CatalogTool
from app.services.mcp.tools import McpProtocolError, McpToolExecutionError
from app.services.rag import RagConfigurationError, RagSearchError

CONFIRMATION_REQUIRED_MCP_TOOLS = {
    "book_flight",
    "book_hotel",
    "cancel_booking",
}


class InvalidFunctionArgumentsError(ValueError):
    pass


def _normalize_tool_result(result: object) -> object:
    if not isinstance(result, dict):
        return result

    structured_content = result.get("structured_content")
    if isinstance(structured_content, (dict, list)):
        return structured_content

    content = result.get("content")
    if not isinstance(content, list) or len(content) != 1:
        return result

    content_item = content[0]
    if not isinstance(content_item, dict) or content_item.get("type") != "text":
        return result

    text = content_item.get("text")
    if not isinstance(text, str):
        return result

    try:
        parsed_text = json.loads(text)
    except json.JSONDecodeError:
        return result
    if isinstance(parsed_text, (dict, list)):
        return parsed_text
    return result


def _parse_function_arguments(arguments_json: str) -> dict:
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as exc:
        raise InvalidFunctionArgumentsError(
            "Los argumentos de la función no son un JSON válido"
        ) from exc

    if not isinstance(arguments, dict):
        raise InvalidFunctionArgumentsError(
            "Los argumentos de la función deben ser un objeto JSON"
        )

    return arguments


def _build_error_result(
    function_call: llm_pb2.FunctionCall,
    error_message: str,
) -> llm_pb2.FunctionResult:
    return llm_pb2.FunctionResult(
        name=function_call.name,
        result_json=json.dumps({"error": error_message}, ensure_ascii=False),
        id=function_call.id,
        is_error=True,
    )


def _requires_confirmation(
    catalog: list[CatalogTool],
    llm_name: str,
) -> bool:
    return any(
        tool.llm_name == llm_name
        and tool.mcp_tool_name in CONFIRMATION_REQUIRED_MCP_TOOLS
        for tool in catalog
    )


async def _dispatch_function_call(
    user_id: str,
    catalog: list[CatalogTool],
    function_call: llm_pb2.FunctionCall,
    arguments: dict,
) -> llm_pb2.FunctionResult:
    try:
        result = await dispatch_tool_call(
            user_id,
            catalog,
            function_call.name,
            arguments,
        )
    except (
        InvalidToolArgumentsError,
        McpToolExecutionError,
        RagConfigurationError,
        RagSearchError,
        UnknownCatalogToolError,
    ) as exc:
        return _build_error_result(function_call, str(exc))
    except McpProtocolError:
        return _build_error_result(
            function_call,
            "No se pudo completar la comunicación con el servidor MCP",
        )

    normalized_result = _normalize_tool_result(result)
    try:
        result_json = json.dumps(normalized_result, ensure_ascii=False)
    except (TypeError, ValueError):
        return _build_error_result(
            function_call,
            "La tool MCP devolvió un resultado que no es JSON válido",
        )

    return llm_pb2.FunctionResult(
        name=function_call.name,
        result_json=result_json,
        id=function_call.id,
        is_error=False,
    )


async def _execute_function_call(
    user_id: str,
    catalog: list[CatalogTool],
    function_call: llm_pb2.FunctionCall,
) -> llm_pb2.FunctionResult:
    try:
        arguments = _parse_function_arguments(function_call.arguments_json)
    except InvalidFunctionArgumentsError as exc:
        return _build_error_result(function_call, str(exc))

    if _requires_confirmation(catalog, function_call.name):
        return _build_error_result(
            function_call,
            "La operación requiere confirmación explícita del usuario",
        )

    return await _dispatch_function_call(
        user_id,
        catalog,
        function_call,
        arguments,
    )


async def execute_approved_tool(
    user_id: str,
    confirmation: dict,
) -> llm_pb2.FunctionResult:
    try:
        function_call_id = confirmation["function_call_id"]
        llm_name = confirmation["llm_name"]
        arguments = confirmation["arguments_json"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "La confirmación aprobada tiene una estructura inválida"
        ) from exc

    if (
        not isinstance(function_call_id, str)
        or not function_call_id
        or not isinstance(llm_name, str)
        or not llm_name
        or not isinstance(arguments, dict)
    ):
        raise ValueError(
            "La confirmación aprobada tiene una estructura inválida"
        )

    catalog = await build_tool_catalog(user_id)
    if not _requires_confirmation(catalog, llm_name):
        raise ValueError("La tool aprobada no requiere confirmación")

    function_call = llm_pb2.FunctionCall(
        id=function_call_id,
        name=llm_name,
        arguments_json=json.dumps(
            arguments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
    return await _dispatch_function_call(
        user_id,
        catalog,
        function_call,
        arguments,
    )


def find_pending_confirmations(
    catalog: list[CatalogTool],
    function_calls: Iterable[llm_pb2.FunctionCall],
) -> tuple[PendingToolConfirmation, ...]:
    pending_confirmations: list[PendingToolConfirmation] = []

    for function_call in function_calls:
        if not _requires_confirmation(catalog, function_call.name):
            continue

        try:
            arguments = _parse_function_arguments(
                function_call.arguments_json
            )
        except InvalidFunctionArgumentsError:
            continue

        arguments_json = json.dumps(
            arguments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        pending_confirmations.append(
            PendingToolConfirmation(
                function_call_id=function_call.id,
                llm_name=function_call.name,
                arguments_json=arguments_json,
            )
        )

    return tuple(pending_confirmations)


async def build_tool_exchange(
    user_id: str,
    catalog: list[CatalogTool],
    response: llm_pb2.GenerateResponse,
    deferred_call_ids: frozenset[str] = frozenset(),
) -> list[llm_pb2.Message]:
    function_results = []
    for function_call in response.function_calls:
        if function_call.id in deferred_call_ids:
            continue
        function_results.append(
            await _execute_function_call(user_id, catalog, function_call)
        )

    model_message = llm_pb2.Message(
        role=llm_pb2.Message.MODEL,
        text=response.text,
        function_calls=response.function_calls,
    )
    exchange = [model_message]
    if function_results:
        exchange.append(
            llm_pb2.Message(
                role=llm_pb2.Message.TOOL,
                function_results=function_results,
            )
        )
    return exchange
