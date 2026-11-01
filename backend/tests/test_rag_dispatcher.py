import json
import unittest
from unittest.mock import AsyncMock, patch

import llm_pb2
from app.services.agent.dispatcher import dispatch_tool_call
from app.services.agent.service import _enforce_rag_rejection
from app.services.agent.tool_calls import (
    _normalize_catalog_tool_result,
    _normalize_tool_result,
    build_tool_exchange,
)
from app.services.mcp.dispatcher import InvalidToolArgumentsError
from app.services.mcp.models import CatalogTool
from app.services.rag import RAG_TOOL_NAME
from app.services.rag.catalog import REJECTION_SENTENCE


class RagDispatcherTests(unittest.IsolatedAsyncioTestCase):
    def test_unwraps_json_text_from_mcp_result_for_llm(self) -> None:
        result = {
            "content": [
                {
                    "type": "text",
                    "text": '{"flights":[{"flightId":"flight-1"}]}',
                }
            ],
            "structured_content": None,
            "is_error": False,
        }

        self.assertEqual(
            _normalize_tool_result(result),
            {"flights": [{"flightId": "flight-1"}]},
        )

    def test_preserves_non_json_mcp_text_result(self) -> None:
        result = {
            "content": [{"type": "text", "text": "Resultado legible"}],
            "structured_content": None,
        }

        self.assertIs(_normalize_tool_result(result), result)

    def test_prefers_structured_mcp_content(self) -> None:
        result = {
            "content": [{"type": "text", "text": '{"value":"fallback"}'}],
            "structured_content": {"value": "structured"},
        }

        self.assertEqual(
            _normalize_tool_result(result),
            {"value": "structured"},
        )

    def test_normalizes_negative_minutes_from_flight_search(self) -> None:
        catalog = [
            CatalogTool(
                llm_name="pre_search_flights",
                description="Busca vuelos",
                input_schema_json="{}",
                server_name="andes-air",
                mcp_tool_name="search_flights",
            )
        ]
        result = {
            "flights": [
                {"depart": "17:-55", "arrive": "05:-43"},
                {"depart": "07:-3", "arrive": "19:38"},
            ]
        }

        normalized = _normalize_catalog_tool_result(
            catalog,
            "pre_search_flights",
            result,
        )

        self.assertEqual(
            normalized,
            {
                "flights": [
                    {"depart": "17:55", "arrive": "05:43"},
                    {"depart": "07:03", "arrive": "19:38"},
                ]
            },
        )
        self.assertEqual(result["flights"][0]["depart"], "17:-55")

    def test_does_not_normalize_times_from_other_tools(self) -> None:
        catalog = [
            CatalogTool(
                llm_name="pre_search_hotels",
                description="Busca hoteles",
                input_schema_json="{}",
                server_name="andes-hotels",
                mcp_tool_name="search_hotels",
            )
        ]
        result = {"flights": [{"depart": "17:-55"}]}

        normalized = _normalize_catalog_tool_result(
            catalog,
            "pre_search_hotels",
            result,
        )

        self.assertIs(normalized, result)

    def test_enforces_exact_rejection_in_combined_response(self) -> None:
        messages = [
            llm_pb2.Message(
                role=llm_pb2.Message.USER,
                text="Reserva el vuelo y revisa las revistas",
            ),
            llm_pb2.Message(
                role=llm_pb2.Message.TOOL,
                function_results=[
                    llm_pb2.FunctionResult(
                        name=RAG_TOOL_NAME,
                        result_json=(
                            '{"fragments":[],"response_mode":"reject"}'
                        ),
                        id="rag-call",
                    )
                ],
            ),
        ]

        result = _enforce_rag_rejection(
            "He reservado tu vuelo.\n"
            "No encontré información específica en las revistas sobre Cancún.",
            messages,
        )

        self.assertEqual(
            result,
            f"He reservado tu vuelo.\n{REJECTION_SENTENCE}",
        )

    async def test_dispatches_local_rag_without_calling_mcp(self) -> None:
        catalog = [
            CatalogTool(
                llm_name=RAG_TOOL_NAME,
                description="Busca revistas",
                input_schema_json="{}",
                source="local",
            )
        ]
        expected = {"fragments": []}

        with patch(
            "app.services.agent.dispatcher.search_magazines",
            new=AsyncMock(return_value=expected),
        ) as rag_search, patch(
            "app.services.agent.dispatcher.dispatch_mcp_tool_call",
            new=AsyncMock(),
        ) as mcp_dispatch:
            result = await dispatch_tool_call(
                "user-1",
                catalog,
                RAG_TOOL_NAME,
                {"queries": ["playas"]},
            )

        self.assertEqual(result, expected)
        rag_search.assert_awaited_once_with({"queries": ["playas"]})
        mcp_dispatch.assert_not_awaited()

    async def test_translates_invalid_local_arguments(self) -> None:
        catalog = [
            CatalogTool(
                llm_name=RAG_TOOL_NAME,
                description="Busca revistas",
                input_schema_json="{}",
                source="local",
            )
        ]

        with patch(
            "app.services.agent.dispatcher.search_magazines",
            new=AsyncMock(side_effect=ValueError("queries inválidas")),
        ), self.assertRaises(InvalidToolArgumentsError):
            await dispatch_tool_call(
                "user-1",
                catalog,
                RAG_TOOL_NAME,
                {"queries": []},
            )

    async def test_preserves_mcp_dispatch(self) -> None:
        catalog = [
            CatalogTool(
                llm_name="pre_search_flights",
                description="Busca vuelos",
                input_schema_json="{}",
                server_name="andes-air",
                mcp_tool_name="search_flights",
            )
        ]
        expected = {"flights": []}

        with patch(
            "app.services.agent.dispatcher.dispatch_mcp_tool_call",
            new=AsyncMock(return_value=expected),
        ) as mcp_dispatch:
            result = await dispatch_tool_call(
                "user-1",
                catalog,
                "pre_search_flights",
                {"origin": "SCL"},
            )

        self.assertEqual(result, expected)
        mcp_dispatch.assert_awaited_once_with(
            "user-1",
            catalog,
            "pre_search_flights",
            {"origin": "SCL"},
        )

    async def test_executes_rag_while_deferring_confirmable_tool(self) -> None:
        catalog = [
            CatalogTool(
                llm_name=RAG_TOOL_NAME,
                description="Busca revistas",
                input_schema_json="{}",
                source="local",
            ),
            CatalogTool(
                llm_name="pre_book_flight",
                description="Reserva un vuelo",
                input_schema_json="{}",
                server_name="andes-air",
                mcp_tool_name="book_flight",
            ),
        ]
        response = llm_pb2.GenerateResponse(
            function_calls=[
                llm_pb2.FunctionCall(
                    id="call-rag",
                    name=RAG_TOOL_NAME,
                    arguments_json='{"queries":["qué hacer en Lima"]}',
                ),
                llm_pb2.FunctionCall(
                    id="call-book",
                    name="pre_book_flight",
                    arguments_json='{"flight_id":"flight-1"}',
                ),
            ],
            stop=False,
        )
        dispatcher = AsyncMock(return_value={"fragments": [{"id": "chunk-1"}]})

        with patch(
            "app.services.agent.tool_calls.dispatch_tool_call",
            new=dispatcher,
        ):
            exchange = await build_tool_exchange(
                "user-1",
                catalog,
                response,
                deferred_call_ids=frozenset({"call-book"}),
            )

        self.assertEqual(
            [message.role for message in exchange],
            [llm_pb2.Message.MODEL, llm_pb2.Message.TOOL],
        )
        function_results = exchange[1].function_results
        self.assertEqual([result.id for result in function_results], ["call-rag"])
        self.assertEqual(
            json.loads(function_results[0].result_json),
            {"fragments": [{"id": "chunk-1"}]},
        )
        dispatcher.assert_awaited_once_with(
            "user-1",
            catalog,
            RAG_TOOL_NAME,
            {"queries": ["qué hacer en Lima"]},
        )


if __name__ == "__main__":
    unittest.main()
