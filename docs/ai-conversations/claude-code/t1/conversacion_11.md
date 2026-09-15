# Conversación 11

Prompt: Tengo un error al conectarme a un servidor MCP remoto (streamable HTTP) usando el SDK oficial de Python (mcp). El script de prueba está en scripts/probar_tools.py, y la función que falla es fetch_tools en app/services/mcp_client.py.

El error ocurre en session.initialize():

mcp.shared.exceptions.MCPError: MCPError(-32603, 'Server returned an error response', None)

-32603 es "Internal error" de JSON-RPC, sin más detalle (data=None). El servidor SÍ responde (confirmé con curl que la URL https://tarea1-mcp-pre-z2fqxmm2ja-uc.a.run.app/mcp existe y devuelve 401 sin auth, con header WWW-Authenticate: Bearer resource_metadata="https://tarea1-mcp-pre-z2fqxmm2ja-uc.a.run.app/.well-known/oauth-protected-resource/mcp", scope="mcp:tools"), pero falla específicamente al mandar el initialize con el access_token como Bearer.

Investiga:

Si el SDK instalado (revisa versión con pip show mcp) está mandando el header MCP-Protocol-Version u otros headers requeridos por el spec de streamable HTTP, y si falta alguno.
Activa logging DEBUG de httpx en el script de prueba para ver el request/response HTTP crudo del initialize, y revisa qué dice el body de la respuesta de error del servidor (no solo el JSON-RPC envuelto por el SDK).
Revisa si la versión de protocolo que el ClientSession/streamable_http_client anuncia por defecto es compatible, o si hay que pasarla explícitamente.
Revisa el resource_metadata del header WWW-Authenticate (GET https://tarea1-mcp-pre-z2fqxmm2ja-uc.a.run.app/.well-known/oauth-protected-resource/mcp) por si el MCP espera un resource o audience específico en el token que no está calzando.

Corrige app/services/mcp_client.py según lo que encuentres. No toques nada de mcp_connection_service.py ni la lógica de OAuth — el token ya se obtiene correctamente, el problema es específico de la llamada al protocolo MCP en sí.

Al terminar, corre python -m scripts.probar_tools y muéstrame el resultado.

Respuesta: Diagnóstico
El problema no está en el protocolo MCP. La versión ni los headers son la causa: probé initialize crudo con 2025-06-18, 2025-03-26 y 2024-11-05, todos con MCP-Protocol-Version y Accept: application/json, text/event-stream, y los tres devuelven lo mismo:


401 {"error":"invalid_token"}
www-authenticate: Bearer resource_metadata="...", scope="mcp:tools"
El -32603 es un artefacto del SDK: en streamable_http.py:370 cualquier status ≥400 que no traiga un cuerpo JSON-RPC se convierte en INTERNAL_ERROR genérico. Por eso data=None — el 401 real quedaba oculto.

La causa real es el access_token. Decodificando el JWT que entrega get_valid_access_token:


{ "scope": "openid", "aud": "https://tarea1-mcp-pre-z2fqxmm2ja-uc.a.run.app", ... }
Dos desajustes contra los metadatos del recurso y del AS:

Token actual	Lo que exige el servidor
scope	openid	mcp:tools (único valor en scopes_supported del AS)
aud	https://…run.app	https://…run.app/mcp (campo resource del oauth-protected-resource)
Ambos vienen del flujo de autorización: authorization_code.py:23 tiene scope: str = "openid" por defecto y mcp_connection_service.py:102 pasa resource=mcp_server["mcp_url"], que es el origen sin /mcp. Verifiqué que un refresh_token con scope=mcp:tools no arregla nada: el AS mantiene el scope del grant original (openid), así que hace falta re-autorizar desde cero.

Lo que sí corregí
Reescribí mcp_client.py:

httpx → httpx2: el SDK 2.0.0 usa httpx2 internamente (isinstance checks, httpx2.StreamError). Pasarle un httpx.AsyncClient 0.28 era un cliente del tipo equivocado. Ahora uso create_mcp_http_client(headers=...), que además aplica los timeouts SSE recomendados y follow_redirects.
Header hook: registra status, cuerpo crudo y www-authenticate de cualquier respuesta ≥400, para que un 401 no vuelva a disfrazarse de -32603.
Saqué el print de debug y el try/except que solo re-lanzaba.
Los headers de protocolo (Accept, MCP-Protocol-Version) los pone el transporte; el cliente solo aporta Authorization, que es lo correcto (los defaults del cliente tienen precedencia sobre los del SDK).
python -m scripts.probar_tools ahora falla igual, pero con la causa visible en el log:


ERROR:app.services.mcp_client:El servidor MCP respondió 401 en https://tarea1-mcp-pre-z2fqxmm2ja-uc.a.run.app/mcp:
{"error":"invalid_token"} | www-authenticate=Bearer resource_metadata="...", scope="mcp:tools"