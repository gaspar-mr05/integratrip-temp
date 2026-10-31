import asyncio
import logging
from functools import lru_cache

import numpy as np
from app.config import get_settings

NOMIC_EMBEDDING_MODEL = "gte-multilingual-base"
MAX_QUERIES = 3
NEIGHBORS_PER_QUERY = 5
MAX_FRAGMENTS = 4
MAX_FRAGMENT_CHARACTERS = 2000

logger = logging.getLogger(__name__)


class RagConfigurationError(RuntimeError):
    pass


class RagSearchError(RuntimeError):
    pass


def _normalize_queries(value: object) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_QUERIES:
        raise ValueError("queries debe contener entre una y tres consultas")

    normalized: list[str] = []
    for query in value:
        if not isinstance(query, str):
            raise TypeError("Cada consulta debe ser texto")
        query = " ".join(query.split())
        if not query or len(query) > 300:
            raise ValueError(
                "Cada consulta debe contener entre 1 y 300 caracteres"
            )
        if query not in normalized:
            normalized.append(query)
    return normalized


def _rank_neighbor_ids(
    neighbors: object,
    distances: object,
) -> list[str]:
    if not isinstance(neighbors, list) or not isinstance(distances, list):
        raise RagSearchError("Nomic devolvió vecinos con un formato inválido")
    if len(neighbors) != len(distances):
        raise RagSearchError("Nomic devolvió resultados inconsistentes")

    ranked: list[tuple[float, str]] = []
    for query_neighbors, query_distances in zip(neighbors, distances):
        if not isinstance(query_neighbors, list) or not isinstance(
            query_distances, list
        ):
            raise RagSearchError("Nomic devolvió vecinos con un formato inválido")
        if len(query_neighbors) != len(query_distances):
            raise RagSearchError("Nomic devolvió resultados inconsistentes")

        for neighbor_id, distance in zip(query_neighbors, query_distances):
            if not isinstance(neighbor_id, str) or not isinstance(
                distance, (int, float)
            ):
                raise RagSearchError("Nomic devolvió un vecino inválido")
            ranked.append((float(distance), neighbor_id))

    unique_ids: list[str] = []
    for _, neighbor_id in sorted(ranked):
        if neighbor_id not in unique_ids:
            unique_ids.append(neighbor_id)
        if len(unique_ids) == MAX_FRAGMENTS:
            break
    return unique_ids


def _build_fragments(rows: object, ranked_ids: list[str]) -> list[dict]:
    if not isinstance(rows, list):
        raise RagSearchError("Nomic devolvió datos con un formato inválido")

    rows_by_id: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RagSearchError("Nomic devolvió un fragmento inválido")
        row_id = row.get("id")
        if not isinstance(row_id, str):
            raise RagSearchError("Nomic devolvió un fragmento sin id")
        rows_by_id[row_id] = row

    fragments: list[dict] = []
    for row_id in ranked_ids:
        row = rows_by_id.get(row_id)
        if row is None:
            raise RagSearchError("Nomic no devolvió todos los fragmentos solicitados")

        text = row.get("text")
        source = row.get("source")
        issue = row.get("issue")
        headings = row.get("headings")
        pages = row.get("pages")
        if (
            not isinstance(text, str)
            or not text.strip()
            or not isinstance(source, str)
            or not isinstance(issue, int)
            or not isinstance(headings, str)
            or not isinstance(pages, str)
        ):
            raise RagSearchError("Nomic devolvió metadatos de fragmento inválidos")

        fragments.append(
            {
                "id": row_id,
                "source": source,
                "issue": issue,
                "headings": headings,
                "pages": pages,
                "text": text[:MAX_FRAGMENT_CHARACTERS],
            }
        )
    return fragments


@lru_cache
def _nomic_resources():
    from nomic import AtlasDataset, login

    settings = get_settings()
    if not settings.NOMIC_API_KEY or not settings.NOMIC_DATASET_IDENTIFIER:
        raise RagConfigurationError(
            "La búsqueda de revistas no está configurada"
        )

    login(settings.NOMIC_API_KEY)
    dataset = AtlasDataset(identifier=settings.NOMIC_DATASET_IDENTIFIER)
    return dataset, dataset.get_map()


def _search_sync(queries: list[str]) -> list[dict]:
    from nomic import embed

    try:
        dataset, projection = _nomic_resources()
        embedding_response = embed.text(
            texts=queries,
            model=NOMIC_EMBEDDING_MODEL,
            task_type="search_query",
        )
        embeddings = embedding_response.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(queries):
            raise RagSearchError("Nomic devolvió embeddings inválidos")

        neighbors, distances = projection.vector_search(
            queries=np.asarray(embeddings, dtype=float),
            k=NEIGHBORS_PER_QUERY,
        )
        ranked_ids = _rank_neighbor_ids(neighbors, distances)
        rows = dataset.get_data(ids=ranked_ids)
        return _build_fragments(rows, ranked_ids)
    except (RagConfigurationError, RagSearchError):
        raise
    except Exception as exc:
        logger.exception("Falló la búsqueda de revistas en Nomic")
        raise RagSearchError(
            "No se pudo completar la búsqueda de revistas"
        ) from exc


async def search_magazines(arguments: dict) -> dict:
    if not isinstance(arguments, dict) or set(arguments) != {"queries"}:
        raise ValueError("La tool requiere únicamente el campo queries")

    queries = _normalize_queries(arguments["queries"])
    fragments = await asyncio.to_thread(_search_sync, queries)
    return {
        "queries": queries,
        "fragments": fragments,
        "answer_policy": (
            "Responde únicamente con información respaldada por estos fragmentos "
            "y cita revista y páginas. Si no son suficientes, responde exactamente: "
            "No encontré información suficiente en las revistas proporcionadas."
        ),
    }
