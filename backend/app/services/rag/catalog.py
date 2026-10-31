import json

from app.services.mcp.models import CatalogTool

RAG_TOOL_NAME = "rag_search_magazines"

_DESCRIPTION = (
    "Busca información verificada sobre destinos, gastronomía, cultura y viajes "
    "en las revistas Traveling. Antes de llamar, limpia la pregunta y divídela "
    "en una a tres consultas de búsqueda específicas cuando tenga varias partes. "
    "La respuesta final debe usar exclusivamente los fragmentos devueltos y citar "
    "la revista y las páginas. Si los fragmentos no permiten responder, responde "
    "exactamente: No encontré información suficiente en las revistas proporcionadas."
)

_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "description": (
                "Una a tres consultas breves, autocontenidas y optimizadas para "
                "búsqueda semántica."
            ),
            "items": {"type": "string", "minLength": 1, "maxLength": 300},
            "minItems": 1,
            "maxItems": 3,
        }
    },
    "required": ["queries"],
    "additionalProperties": False,
}


def build_rag_catalog_tool() -> CatalogTool:
    return CatalogTool(
        llm_name=RAG_TOOL_NAME,
        description=_DESCRIPTION,
        input_schema_json=json.dumps(_INPUT_SCHEMA, ensure_ascii=False),
        source="local",
    )
