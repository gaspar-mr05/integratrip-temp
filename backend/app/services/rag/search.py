import asyncio
import logging
import re
import unicodedata
from functools import lru_cache

import requests

from app.config import get_settings
from app.services.rag.catalog import build_answer_policy

NOMIC_EMBEDDING_MODEL = "gte-multilingual-base"
MAX_QUERIES = 3
NEIGHBORS_PER_QUERY = 5
MAX_FRAGMENTS = 4
MAX_FRAGMENT_CHARACTERS = 2000
NOMIC_REQUEST_TIMEOUT_SECONDS = 30

logger = logging.getLogger(__name__)

_LOCATION_PATTERN = re.compile(
    r"\b(?:en|del|de la|de los|de las|de)\s+"
    r"(?:el\s+|la\s+|los\s+|las\s+)?"
    r"([A-ZÁÉÍÓÚÜÑ][\wÁÉÍÓÚÜÑáéíóúüñ-]*"
    r"(?:\s+(?:de|del|la|las|los|y|[A-ZÁÉÍÓÚÜÑ][\wÁÉÍÓÚÜÑáéíóúüñ-]*))*)"
)


class RagConfigurationError(RuntimeError):
    pass


class RagSearchError(RuntimeError):
    pass


def _normalize_for_matching(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return " ".join(
        without_accents.casefold().split()
    )


def _extract_location_anchors(queries: list[str]) -> list[str]:
    anchors: list[str] = []
    for query in queries:
        for match in _LOCATION_PATTERN.finditer(query):
            anchor = _normalize_for_matching(match.group(1))
            if anchor not in anchors:
                anchors.append(anchor)
    return anchors


def _filter_fragments_by_location(
    fragments: list[dict],
    queries: list[str],
) -> list[dict]:
    anchors = _extract_location_anchors(queries)
    if not anchors:
        return fragments

    filtered: list[dict] = []
    for fragment in fragments:
        searchable_text = _normalize_for_matching(
            f"{fragment['headings']} {fragment['text']}"
        )
        if any(anchor in searchable_text for anchor in anchors):
            filtered.append(fragment)
    return filtered


def _response_mode(queries: list[str], fragments: list[dict]) -> str:
    if not fragments:
        return "reject"
    if _extract_location_anchors(queries):
        return "answer"
    return "evaluate"


def _normalize_queries(value: object) -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_QUERIES:
        raise ValueError("queries debe contener entre una y tres consultas")

    normalized: list[str] = []
    for query in value:
        if not isinstance(query, str):
            raise TypeError("Cada consulta debe ser texto")
        query = " ".join(query.split())
        if not query or len(query) > 300:
            raise ValueError("Cada consulta debe contener entre 1 y 300 caracteres")
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


def _vector_search(projection, embeddings: list) -> tuple[object, object]:
    dataset = projection.dataset
    response = requests.post(
        f"{dataset.atlas_api_path}/v1/project/data/get/nearest_neighbors/by_embedding",
        headers=dataset.header,
        json={
            "atlas_index_id": projection.atlas_index_id,
            "queries": embeddings,
            "k": NEIGHBORS_PER_QUERY,
        },
        timeout=NOMIC_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RagSearchError("Nomic devolvió una respuesta inválida")

    neighbors = payload.get("neighbors")
    distances = payload.get("distances")
    if neighbors is None or distances is None:
        raise RagSearchError("Nomic devolvió una respuesta incompleta")
    return neighbors, distances


@lru_cache
def _nomic_resources():
    from nomic import AtlasDataset, login

    settings = get_settings()
    api_key = settings.NOMIC_API_KEY.strip() if settings.NOMIC_API_KEY else ""
    dataset_identifier = (
        settings.NOMIC_DATASET_IDENTIFIER.strip()
        if settings.NOMIC_DATASET_IDENTIFIER
        else ""
    )
    if not api_key or not dataset_identifier:
        raise RagConfigurationError("La búsqueda de revistas no está configurada")

    login(api_key)
    dataset = AtlasDataset(identifier=dataset_identifier)
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

        neighbors, distances = _vector_search(projection, embeddings)
        ranked_ids = _rank_neighbor_ids(neighbors, distances)
        rows = dataset.get_data(ids=ranked_ids)
        fragments = _build_fragments(rows, ranked_ids)
        return _filter_fragments_by_location(fragments, queries)
    except (RagConfigurationError, RagSearchError):
        raise
    except Exception as exc:
        logger.error(
            "Falló la búsqueda de revistas en Nomic (%s)",
            type(exc).__name__,
        )
        raise RagSearchError("No se pudo completar la búsqueda de revistas") from exc


async def search_magazines(arguments: dict) -> dict:
    if not isinstance(arguments, dict) or set(arguments) != {"queries"}:
        raise ValueError("La tool requiere únicamente el campo queries")

    queries = _normalize_queries(arguments["queries"])
    fragments = await asyncio.to_thread(_search_sync, queries)
    response_mode = _response_mode(queries, fragments)
    return {
        "queries": queries,
        "fragments": fragments,
        "response_mode": response_mode,
        "answer_policy": build_answer_policy(response_mode),
    }
