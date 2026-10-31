# IntegraTrip / MagnaTrip

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```


URL para acceder a la página: https://integratrip-temp.vercel.app

## Base de conocimiento de revistas

Las ediciones seleccionadas para la Tarea 3 son las revistas 69 a 78.

Los PDF se descargan localmente y no se versionan. Los archivos JSONL procesados
sí quedan en `backend/data/magazines/processed`.

```bash
cd backend
pip install -r requirements-rag.txt
python -m scripts.rag.download_magazines
python -m scripts.rag.parse_magazines
```

Para crear el dataset público y su índice con `gte-multilingual-base`:

```bash
export NOMIC_API_KEY="..."
export NOMIC_DATASET_IDENTIFIER="organizacion/integratrip-magazines"
python -m scripts.rag.upload_nomic
```
