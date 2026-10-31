import json
import unittest

from app.services.rag.catalog import RAG_TOOL_NAME, build_rag_catalog_tool
from app.services.rag.search import (
    RagSearchError,
    _build_fragments,
    _normalize_queries,
    _rank_neighbor_ids,
)


class RagSearchTests(unittest.TestCase):
    def test_catalog_requests_decomposed_queries(self) -> None:
        tool = build_rag_catalog_tool()
        schema = json.loads(tool.input_schema_json)

        self.assertEqual(tool.llm_name, RAG_TOOL_NAME)
        self.assertEqual(tool.source, "local")
        self.assertEqual(schema["properties"]["queries"]["maxItems"], 3)

    def test_normalizes_and_deduplicates_queries(self) -> None:
        queries = _normalize_queries(
            ["  playas   tranquilas ", "playas tranquilas", "castillos"]
        )

        self.assertEqual(queries, ["playas tranquilas", "castillos"])

    def test_rejects_invalid_queries(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_queries([])
        with self.assertRaises(TypeError):
            _normalize_queries(["válida", 2])

    def test_ranks_and_deduplicates_four_nearest_neighbors(self) -> None:
        ranked_ids = _rank_neighbor_ids(
            [["chunk-1", "chunk-2", "chunk-3"], ["chunk-2", "chunk-4", "chunk-5"]],
            [[0.3, 0.2, 0.6], [0.1, 0.4, 0.5]],
        )

        self.assertEqual(
            ranked_ids,
            ["chunk-2", "chunk-1", "chunk-4", "chunk-5"],
        )

    def test_builds_fragments_in_ranked_order_and_truncates_text(self) -> None:
        rows = [
            {
                "id": "chunk-1",
                "text": "a" * 2100,
                "source": "traveling69.pdf",
                "issue": 69,
                "headings": "Chile",
                "pages": "4,5",
            },
            {
                "id": "chunk-2",
                "text": "Texto dos",
                "source": "traveling70.pdf",
                "issue": 70,
                "headings": "España",
                "pages": "10",
            },
        ]

        fragments = _build_fragments(rows, ["chunk-2", "chunk-1"])

        self.assertEqual([item["id"] for item in fragments], ["chunk-2", "chunk-1"])
        self.assertEqual(len(fragments[1]["text"]), 2000)

    def test_rejects_missing_neighbor_data(self) -> None:
        with self.assertRaises(RagSearchError):
            _build_fragments([], ["missing"])


if __name__ == "__main__":
    unittest.main()
