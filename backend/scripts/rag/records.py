import json
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path


class InvalidChunkRecordError(ValueError):
    pass


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    text: str
    source: str
    issue: int
    headings: str
    pages: str

    def __post_init__(self) -> None:
        if not self.id or len(self.id) > 36:
            raise InvalidChunkRecordError(
                "El id del chunk debe contener entre 1 y 36 caracteres"
            )
        if not self.text.strip():
            raise InvalidChunkRecordError("El texto del chunk no puede estar vacío")
        if not self.source.strip():
            raise InvalidChunkRecordError("La fuente del chunk no puede estar vacía")
        if self.issue <= 0:
            raise InvalidChunkRecordError("El número de revista debe ser positivo")
        if not self.pages.strip():
            raise InvalidChunkRecordError("El chunk debe indicar al menos una página")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: object) -> "ChunkRecord":
        if not isinstance(value, dict):
            raise InvalidChunkRecordError("Cada registro JSONL debe ser un objeto")

        expected_fields = {"id", "text", "source", "issue", "headings", "pages"}
        if set(value) != expected_fields:
            raise InvalidChunkRecordError(
                "El registro JSONL no contiene exactamente los campos requeridos"
            )

        try:
            return cls(**value)
        except TypeError as exc:
            raise InvalidChunkRecordError(
                "El registro JSONL contiene tipos de datos inválidos"
            ) from exc


def build_chunk_record(
    *,
    issue: int,
    sequence: int,
    text: str,
    source: str,
    headings: Iterable[str],
    pages: Iterable[int],
) -> ChunkRecord:
    normalized_pages = sorted(set(pages))
    return ChunkRecord(
        id=f"traveling{issue}-{sequence:05d}",
        text=text.strip(),
        source=source,
        issue=issue,
        headings=" > ".join(heading.strip() for heading in headings if heading.strip()),
        pages=",".join(str(page) for page in normalized_pages),
    )


def write_jsonl(path: Path, records: Iterable[ChunkRecord]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.part")
    count = 0

    with temporary_path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record.to_dict(), ensure_ascii=False))
            output.write("\n")
            count += 1

    if count == 0:
        temporary_path.unlink(missing_ok=True)
        raise InvalidChunkRecordError("No se generaron chunks para la revista")

    temporary_path.replace(path)
    return count


def read_jsonl(paths: Iterable[Path]) -> Iterator[ChunkRecord]:
    seen_ids: set[str] = set()

    for path in paths:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                try:
                    value = json.loads(line)
                    record = ChunkRecord.from_dict(value)
                except (json.JSONDecodeError, InvalidChunkRecordError) as exc:
                    raise InvalidChunkRecordError(
                        f"Registro inválido en {path}:{line_number}: {exc}"
                    ) from exc

                if record.id in seen_ids:
                    raise InvalidChunkRecordError(
                        f"Se encontró un id de chunk duplicado: {record.id}"
                    )
                seen_ids.add(record.id)
                yield record
