# IntegraTrip

Chat para planificar viajes mediante un agente con herramientas MCP y búsqueda
RAG sobre revistas Traveling.

- Aplicación: <https://integratrip-temp.vercel.app>
- Dataset Nomic: `gasparmagnar/integratrip-magazines`
- Mapa público: <https://atlas.nomic.ai/data/gasparmagnar/integratrip-magazines/map>

## Ejecución local

Requiere Python 3.12 y Node.js 20.19 o superior.

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-rag.txt
uvicorn app.main:app --reload
```

El backend usa las variables definidas en `backend/.env` y queda disponible en
<http://localhost:8000>. Si `.venv` produce un `Segmentation fault`, usar el
entorno existente `.venv-t3`:

```bash
source .venv-t3/bin/activate
uvicorn app.main:app --reload
```

### Frontend

Crear `frontend/.env`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Luego ejecutar:

```bash
cd frontend
npm install
npm run dev
```

El frontend queda disponible en <http://localhost:5173>.

## RAG

Se utilizaron las ediciones **69 a 78** de Traveling Magazine. Los PDF no se
versionan; los chunks JSONL procesados sí están en el repositorio.

Para descargar y procesar las revistas:

```bash
cd backend
source .venv/bin/activate
python -m scripts.rag.download_magazines
python -m scripts.rag.parse_magazines
```

### Exploración en Atlas

- **Temas:** destinos turísticos, gastronomía y vinos, arquitectura medieval y
  modernista, rutas y cultura de viajes.
- **Destinos:** aparecen, entre otros, Algarve, Huelva, Lipari, Costa Rica,
  Asturias, Burgos, La Rioja y Castellón.
- **Clusters:** sí; los principales separan destinos, gastronomía, arquitectura
  y contenido editorial.
- **Chunks duplicados:** sí; hay 18 grupos de texto idéntico (129 chunks),
  principalmente créditos y datos editoriales repetidos entre ediciones.
- **Chunks irrelevantes:** sí; aparecen créditos, contactos, índices y algunos
  fragmentos publicitarios.
- **Búsqueda `playas`:** recupera resultados pertinentes del Algarve, Playa de
  las Catedrales, Playa Naranjo, Canneto y Huelva.
- **Búsqueda `castillos`:** recupera fortalezas y conjuntos medievales como el
  Fuerte de San Felipe, Santa Gadea del Cid y el Castillo de los Velasco en
  Frías.
- **Búsqueda `comida romántica`:** el resultado más relevante es VelascoAbellà,
  descrito como un restaurante apropiado para una cena romántica.

## Verificación

```bash
# Backend, desde backend/
python -m unittest discover -s tests

# Lint del backend, desde la raíz
ruff check backend/app backend/scripts backend/tests

# Frontend, desde frontend/
npm run lint
npm run build
```
