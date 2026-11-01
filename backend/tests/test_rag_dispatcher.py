import json
import unittest
from unittest.mock import AsyncMock, patch

import llm_pb2
from app.services.agent.dispatcher import dispatch_tool_call
from app.services.agent.service import _enforce_rag_rejection
from app.services.agent.tool_calls import build_tool_exchange
from app.services.mcp.dispatcher import InvalidToolArgumentsError
from app.services.mcp.models import CatalogTool
from app.services.rag import RAG_TOOL_NAME
from app.services.rag.catalog import REJECTION_SENTENCE


class RagDispatcherTests(unittest.IsolatedAsyncioTestCase):
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
