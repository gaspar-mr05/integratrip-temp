import argparse
import os
from pathlib import Path

from scripts.rag.records import read_jsonl
from scripts.rag.settings import (
    NOMIC_BATCH_SIZE,
    NOMIC_EMBEDDING_MODEL,
    PROCESSED_MAGAZINES_DIR,
    SELECTED_ISSUES,
)


def _batched(records: list[dict], batch_size: int):
    for start in range(0, len(records), batch_size):
        yield records[start : start + batch_size]


def _validate_selected_issues(records: list[dict]) -> None:
    actual_issues = {record["issue"] for record in records}
    expected_issues = set(SELECTED_ISSUES)
    if actual_issues != expected_issues:
        missing = sorted(expected_issues - actual_issues)
        unexpected = sorted(actual_issues - expected_issues)
        raise ValueError(
            "La selección de revistas está incompleta o no corresponde a la "
            f"configurada; faltantes={missing}, inesperadas={unexpected}"
        )


def upload_dataset(
    *,
    api_key: str,
    identifier: str,
    jsonl_paths: list[Path],
) -> None:
    from nomic import AtlasDataset, login

    records = [record.to_dict() for record in read_jsonl(jsonl_paths)]
    if not records:
        raise ValueError("No se encontraron chunks para subir a Nomic")
    _validate_selected_issues(records)

    login(api_key)
    dataset = AtlasDataset(
        identifier=identifier,
        description="Revistas Traveling para IntegraTrip",
        unique_id_field="id",
        is_public=True,
    )
    if dataset.total_datums:
        raise ValueError(
            f"El dataset {dataset.identifier} ya contiene datos; "
            "usa un identificador nuevo para evitar duplicados"
        )

    uploaded = 0
    for batch in _batched(records, NOMIC_BATCH_SIZE):
        dataset.add_data(data=batch)
        uploaded += len(batch)
        print(f"Subidos {uploaded}/{len(records)} chunks")

    dataset.create_index(
        name=dataset.slug,
        indexed_field="text",
        modality="text",
        embedding_model=NOMIC_EMBEDDING_MODEL,
    )
    print(
        f"Dataset {dataset.identifier} id={dataset.id} "
        f"points={dataset.total_datums}"
    )
    print(f"Mapa: https://atlas.nomic.ai/data/{dataset.identifier}/map")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sube los chunks e inicia el índice público en Nomic Atlas.",
    )
    parser.add_argument(
        "--identifier",
        default=os.getenv("NOMIC_DATASET_IDENTIFIER"),
        help="Identificador dataset u organización/dataset.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROCESSED_MAGAZINES_DIR,
        help="Directorio de archivos travelingNN.jsonl.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    api_key = os.getenv("NOMIC_API_KEY")
    if not api_key:
        raise ValueError("Define NOMIC_API_KEY sin agregarla al repositorio")
    if not args.identifier:
        raise ValueError(
            "Indica --identifier o define NOMIC_DATASET_IDENTIFIER"
        )

    jsonl_paths = sorted(args.input_dir.glob("traveling*.jsonl"))
    if not jsonl_paths:
        raise FileNotFoundError(
            f"No se encontraron archivos JSONL en {args.input_dir}"
        )
    upload_dataset(
        api_key=api_key,
        identifier=args.identifier,
        jsonl_paths=jsonl_paths,
    )


if __name__ == "__main__":
    main()
