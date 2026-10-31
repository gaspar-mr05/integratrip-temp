import json

from app.services.mcp.models import CatalogTool

RAG_TOOL_NAME = "rag_search_magazines"

_DESCRIPTION = (
    "Busca información verificada sobre destinos, gastronomía, cultura y viajes "
    "en las revistas Traveling. Antes de llamar, limpia la pregunta y divídela "
    "en una a tres consultas de búsqueda específicas cuando tenga varias partes. "
    "Las afirmaciones obtenidas de las revistas deben usar exclusivamente los "
    "fragmentos devueltos. Después de cada recomendación basada en ellos, incluye "
    "siempre una cita con el formato (Traveling {issue}, p. {pages}). Puedes "
    "combinar esos "
    "fragmentos con resultados de otras tools para responder otras partes de la "
    "pregunta. Evalúa cada parte de forma independiente: el error de otra tool no "
    "invalida fragmentos útiles de las revistas. Usa la frase de rechazo solo si "
    "ningún fragmento permite responder la parte solicitada a las revistas; en ese "
    "caso, responde "
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
