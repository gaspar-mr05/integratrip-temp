import json

from app.services.mcp.models import CatalogTool

RAG_TOOL_NAME = "rag_search_magazines"
REJECTION_SENTENCE = (
    "No encontré información suficiente en las revistas proporcionadas."
)
QUERY_PLANNING_POLICY = (
    "Genera una consulta separada por cada tema independiente, hasta un máximo "
    "de tres. Nunca combines gastronomía, actividades y lugares en una sola "
    "consulta. Repite el destino en cada consulta para que sean autocontenidas. "
    "Ejemplo: una pregunta sobre comer, senderismo y playas en el Algarve debe "
    "producir tres consultas: gastronomía en el Algarve; senderismo en el "
    "Algarve; playas tranquilas en el Algarve."
)

ANSWER_POLICY = (
    "Reglas obligatorias para la parte solicitada a las revistas: "
    "1) Usa solo fragmentos cuyo texto o encabezado respalde explícitamente el "
    "destino y la recomendación. Ignora otros destinos y nunca les cambies el "
    "nombre. "
    "2) Después de cada recomendación incluye (Traveling {issue}, p. {pages}) "
    "y copia pages sin alterarlo. "
    "3) Obedece response_mode: answer obliga a responder con los fragmentos y "
    "prohíbe la frase de rechazo; reject obliga a usar exactamente la frase de "
    "rechazo; evaluate exige decidir si los fragmentos sirven. "
    "4) En una respuesta combinada puedes responder otras tools, pero mantén "
    "intacta esa oración para la parte de revistas. "
    "5) No uses la frase si el usuario no pidió información de las revistas o "
    "si esta tool no fue ejecutada."
)


def build_answer_policy(response_mode: str) -> str:
    if response_mode == "answer":
        mode_instruction = (
            "response_mode=answer. Los fragmentos ya fueron validados para el "
            "destino solicitado. Debes responder usando esos fragmentos y sus "
            "citas. Está prohibido usar la frase de rechazo."
        )
    elif response_mode == "reject":
        mode_instruction = (
            "response_mode=reject. Para la parte solicitada a las revistas debes "
            f"escribir exactamente, sin añadir ni cambiar palabras: {REJECTION_SENTENCE}"
        )
    elif response_mode == "evaluate":
        mode_instruction = (
            "response_mode=evaluate. Usa solo los fragmentos que respondan la "
            "solicitud. Si ninguno sirve, usa exactamente la frase de rechazo: "
            f"{REJECTION_SENTENCE}"
        )
    else:
        raise ValueError("El modo de respuesta RAG no es válido")

    return f"{ANSWER_POLICY} {mode_instruction}"

_DESCRIPTION = (
    "Busca información verificada sobre destinos, gastronomía, cultura y viajes "
    "en las revistas Traveling. Antes de llamar, limpia la pregunta. "
    + QUERY_PLANNING_POLICY
    + " "
    + ANSWER_POLICY
)

_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "description": (
                "Una a tres consultas breves, autocontenidas y optimizadas para "
                "búsqueda semántica. "
                + QUERY_PLANNING_POLICY
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
