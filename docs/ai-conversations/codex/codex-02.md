# Conversación Codex 02

## Prompt

Usa la skill code-review y revisa únicamente backend/app/services.
No hagas cambios, solo reporta problemas.

## Respuesta

Usaré la skill `code-review` y limitaré estrictamente la inspección a `backend/app/services`; no modificaré archivos. Primero leeré sus instrucciones y luego revisaré el código y las pruebas relevantes solo en ese alcance.

## Respuesta

Ya identifiqué los módulos del alcance. Estoy verificando los flujos OAuth/MCP y sus límites de error, poniendo primero fallos de corrección y seguridad; ignoraré `__pycache__` y detalles meramente estilísticos.

## Respuesta

Encontré 4 problemas relevantes. No hice cambios.

- **Alta — Se confía en un access token sin verificar criptográficamente.**  
  [auth_service.py:85](/home/gaspa/IIC3103/Tareas/T1/backend/app/services/auth_service.py:85) obtiene `sub` mediante `read_unverified_access_token_claims` y luego crea una sesión local. Si el token recibido fuese manipulado o emitido por una fuente no confiable, permitiría suplantar usuarios. Debe verificarse firma, emisor, audiencia y expiración antes de usar los claims.

- **Media — Posible filtración de secretos en logs durante DCR.**  
  [dcr.py:38](/home/gaspa/IIC3103/Tareas/T1/backend/app/services/oauth/dcr.py:38) registra la respuesta completa cuando falta `client_id`. Esa respuesta podría incluir `client_secret` u otros datos sensibles. Se debería registrar únicamente una lista de campos presentes o una versión explícitamente sanitizada.

- **Media — Un refresh exitoso se devuelve aunque falle su persistencia.**  
  [mcp_connection_service.py:187](/home/gaspa/IIC3103/Tareas/T1/backend/app/services/mcp_connection_service.py:187) ignora el resultado de `upsert_mcp_connection`, a diferencia del flujo inicial. El request actual recibe un token válido, pero la conexión queda con el token expirado —o pierde un refresh token rotado— y las llamadas posteriores fallarán. Debe comprobarse el resultado y lanzar `ConnectionFlowError` si no se guardó.

- **Media — Respuestas JSON inválidas escapan del contrato de errores del servicio.**  
  [authorization_code.py:56](/home/gaspa/IIC3103/Tareas/T1/backend/app/services/oauth/authorization_code.py:56) y [dcr.py:36](/home/gaspa/IIC3103/Tareas/T1/backend/app/services/oauth/dcr.py:36) llaman directamente a `response.json()`. Una respuesta 2xx vacía, HTML o JSON malformado produce una excepción de `requests` que no se transforma en `OAuthTokenExchangeError`/`DcrRegistrationError`, probablemente terminando como error 500 inesperado. Conviene capturar el error de decodificación y convertirlo en la excepción de dominio correspondiente.

