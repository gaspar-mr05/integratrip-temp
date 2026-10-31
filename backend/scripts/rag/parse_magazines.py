import argparse
import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from scripts.rag.records import ChunkRecord, build_chunk_record, write_jsonl
from scripts.rag.settings import (
    CHUNK_MAX_TOKENS,
    PROCESSED_MAGAZINES_DIR,
    RAW_MAGAZINES_DIR,
    TOKENIZER_MODEL,
)

_ISSUE_FILENAME_PATTERN = re.compile(r"traveling(?P<issue>[1-9][0-9]*)\.pdf")


def _issue_from_path(path: Path) -> int:
    match = _ISSUE_FILENAME_PATTERN.fullmatch(path.name.lower())
    if match is None:
        raise ValueError(
            f"El archivo debe llamarse travelingNN.pdf: {path.name}"
        )
    return int(match.group("issue"))


def _chunk_pages(chunk: object) -> list[int]:
    meta = chunk.meta
    return [
        provenance.page_no
        for item in meta.doc_items
        for provenance in item.prov
    ]


def _build_converter_and_chunker():
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import (
        HuggingFaceTokenizer,
    )

    pipeline_options = PdfPipelineOptions(do_ocr=False)
    converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        },
    )
    tokenizer = HuggingFaceTokenizer.from_pretrained(
        model_name=TOKENIZER_MODEL,
        max_tokens=CHUNK_MAX_TOKENS,
    )
    return converter, HybridChunker(tokenizer=tokenizer)


def _records_from_chunks(
    *,
    issue: int,
    source: str,
    chunks: Iterable[object],
) -> Iterator[ChunkRecord]:
    for sequence, chunk in enumerate(chunks, start=1):
        meta = chunk.meta
        yield build_chunk_record(
            issue=issue,
            sequence=sequence,
            text=chunk.text,
            source=source,
            headings=meta.headings or (),
            pages=_chunk_pages(chunk),
        )


def parse_magazine(
    pdf_path: Path,
    output_dir: Path,
    converter: object,
    chunker: object,
) -> Path:
    issue = _issue_from_path(pdf_path)
    output_path = output_dir / f"traveling{issue}.jsonl"

    result = converter.convert(pdf_path)
    chunks = chunker.chunk(result.document)
    records = _records_from_chunks(
        issue=issue,
        source=pdf_path.name,
        chunks=chunks,
    )
    count = write_jsonl(output_path, records)
    print(f"Revista {issue}: {count} chunks en {output_path}")
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convierte revistas PDF a chunks JSONL usando Docling.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=RAW_MAGAZINES_DIR,
        help="Directorio que contiene travelingNN.pdf.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROCESSED_MAGAZINES_DIR,
        help="Directorio para los archivos JSONL.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Vuelve a procesar revistas que ya tienen un JSONL completo.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    pdf_paths = sorted(args.input_dir.glob("traveling*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(
            f"No se encontraron revistas PDF en {args.input_dir}"
        )

    pending_paths: list[Path] = []
    for pdf_path in pdf_paths:
        issue = _issue_from_path(pdf_path)
        output_path = args.output_dir / f"traveling{issue}.jsonl"
        if output_path.is_file() and not args.force:
            print(f"Revista {issue}: ya procesada")
            continue
        pending_paths.append(pdf_path)

    if not pending_paths:
        print("Todas las revistas ya están procesadas")
        return

    converter, chunker = _build_converter_and_chunker()
    for pdf_path in pending_paths:
        parse_magazine(
            pdf_path,
            args.output_dir,
            converter,
            chunker,
        )


if __name__ == "__main__":
    main()
