import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.rag.catalog import RAG_TOOL_NAME, build_rag_catalog_tool
from app.services.rag.search import (
    RagSearchError,
    _build_fragments,
    _nomic_resources,
    _normalize_queries,
    _rank_neighbor_ids,
    _search_sync,
    _vector_search,
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

    def test_vector_search_sends_embeddings_as_an_array(self) -> None:
        response = MagicMock()
        response.json.return_value = {
            "neighbors": [["chunk-1"]],
            "distances": [[0.1]],
        }
        projection = SimpleNamespace(
            atlas_index_id="index-1",
            dataset=SimpleNamespace(
                atlas_api_path="https://api-atlas.nomic.ai",
                header={"Authorization": "Bearer hidden"},
            ),
        )

        with patch(
            "app.services.rag.search.requests.post", return_value=response
        ) as post:
            neighbors, distances = _vector_search(projection, [[0.1, 0.2]])

        self.assertEqual(neighbors, [["chunk-1"]])
        self.assertEqual(distances, [[0.1]])
        response.raise_for_status.assert_called_once_with()
        post.assert_called_once_with(
            "https://api-atlas.nomic.ai/v1/project/data/get/nearest_neighbors/by_embedding",
            headers={"Authorization": "Bearer hidden"},
            json={
                "atlas_index_id": "index-1",
                "queries": [[0.1, 0.2]],
                "k": 5,
            },
            timeout=30,
        )

    def test_nomic_resources_strip_configuration_whitespace(self) -> None:
        settings = SimpleNamespace(
            NOMIC_API_KEY="  secret-key\n",
            NOMIC_DATASET_IDENTIFIER=" gasparmagnar/integratrip-magazines\n",
        )
        dataset = MagicMock()

        _nomic_resources.cache_clear()
        try:
            with (
                patch("app.services.rag.search.get_settings", return_value=settings),
                patch("nomic.login") as login,
                patch("nomic.AtlasDataset", return_value=dataset) as atlas_dataset,
            ):
                result = _nomic_resources()
        finally:
            _nomic_resources.cache_clear()

        self.assertEqual(result, (dataset, dataset.get_map.return_value))
        login.assert_called_once_with("secret-key")
        atlas_dataset.assert_called_once_with(
            identifier="gasparmagnar/integratrip-magazines"
        )

    def test_search_fetches_ranked_fragments(self) -> None:
        row = {
            "id": "chunk-1",
            "text": "Una playa tranquila",
            "source": "traveling69.pdf",
            "issue": 69,
            "headings": "Playas",
            "pages": "4",
        }
        projection = SimpleNamespace()
        dataset = MagicMock()
        dataset.get_data.return_value = [row]

        with (
            patch(
                "app.services.rag.search._nomic_resources",
                return_value=(dataset, projection),
            ),
            patch(
                "nomic.embed.text",
                return_value={"embeddings": [[0.1, 0.2]]},
            ),
            patch(
                "app.services.rag.search._vector_search",
                return_value=([["chunk-1"]], [[0.1]]),
            ),
        ):
            fragments = _search_sync(["playas tranquilas"])

        self.assertEqual(fragments[0]["id"], "chunk-1")
        dataset.get_data.assert_called_once_with(ids=["chunk-1"])


if __name__ == "__main__":
    unittest.main()
