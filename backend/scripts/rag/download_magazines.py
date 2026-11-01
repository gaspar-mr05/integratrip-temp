import argparse
from pathlib import Path

import requests

from scripts.rag.settings import (
    MAGAZINE_URL_TEMPLATE,
    RAW_MAGAZINES_DIR,
    SELECTED_ISSUES,
)

DOWNLOAD_CHUNK_SIZE = 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 120


class InvalidMagazineDownloadError(ValueError):
    pass


def _is_pdf(path: Path) -> bool:
    if not path.is_file():
        return False
    with path.open("rb") as source:
        return source.read(5) == b"%PDF-"


def download_magazine(issue: int, output_dir: Path) -> Path:
    if issue <= 0:
        raise ValueError("El número de revista debe ser positivo")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"traveling{issue}.pdf"
    if _is_pdf(output_path):
        print(f"Revista {issue}: ya descargada")
        return output_path

    url = MAGAZINE_URL_TEMPLATE.format(issue=issue)
    temporary_path = output_path.with_suffix(".pdf.part")

    with requests.get(
        url,
        stream=True,
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
    ) as response:
        response.raise_for_status()
        with temporary_path.open("wb") as output:
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk:
                    output.write(chunk)

    if not _is_pdf(temporary_path):
        temporary_path.unlink(missing_ok=True)
        raise InvalidMagazineDownloadError(
            f"La descarga de la revista {issue} no es un archivo PDF válido"
        )

    temporary_path.replace(output_path)
    print(f"Revista {issue}: descargada en {output_path}")
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga las revistas seleccionadas sin versionar los PDF.",
    )
    parser.add_argument(
        "--issues",
        nargs="+",
        type=int,
        default=SELECTED_ISSUES,
        help="Números de revista a descargar.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RAW_MAGAZINES_DIR,
        help="Directorio de destino de los PDF.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    for issue in args.issues:
        download_magazine(issue, args.output_dir)


if __name__ == "__main__":
    main()
