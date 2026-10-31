import unittest
from unittest.mock import AsyncMock, patch

from app.services.agent.dispatcher import dispatch_tool_call
from app.services.mcp.dispatcher import InvalidToolArgumentsError
from app.services.mcp.models import CatalogTool
from app.services.rag import RAG_TOOL_NAME


class RagDispatcherTests(unittest.IsolatedAsyncioTestCase):
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


if __name__ == "__main__":
    unittest.main()
