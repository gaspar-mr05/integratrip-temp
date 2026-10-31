from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
MAGAZINES_DIR = BACKEND_DIR / "data" / "magazines"
RAW_MAGAZINES_DIR = MAGAZINES_DIR / "raw"
PROCESSED_MAGAZINES_DIR = MAGAZINES_DIR / "processed"

SELECTED_ISSUES = tuple(range(69, 79))
MAGAZINE_URL_TEMPLATE = (
    "https://www.tienda-revistatraveling.es/descargas/traveling{issue}.pdf"
)

TOKENIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_MAX_TOKENS = 750
NOMIC_EMBEDDING_MODEL = "gte-multilingual-base"
NOMIC_BATCH_SIZE = 500
