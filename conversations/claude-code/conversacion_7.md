# Conversación 7

**Prompt:** ### Refactor OAuth PRE

Extrae **solo la lógica OAuth PRE genérica** de `auth_service.py` hacia `app/services/oauth/pre.py`.

En `pre.py` crea:

* `build_authorization_url(...)`: recibe por parámetros `authorization_endpoint`, `client_id`, `redirect_uri`, `state`, `code_challenge`, `resource` y `scope="openid"`.
* `exchange_code_for_tokens(...)`: recibe `token_endpoint`, `client_id`, `client_secret`, `redirect_uri`, `code` y `code_verifier`.

Ambas funciones deben usar **keyword-only arguments (`*`)**.

La función de token debe mantener **exactamente** el comportamiento actual de `auth_service.py`: `timeout=10`, manejo de `requests.RequestException`, error si el status no es `200` y los mismos logs. Crea una excepción propia `PreTokenExchangeError`.

Luego modifica `auth_service.py` para usar estas funciones nuevas en `start_login_flow` y `exchange_code_for_tokens`.

**No modifiques routers, DB, DCR, CIMD ni implementes conexión a MCPs. Todo lo demás de `auth_service.py` debe quedar igual.**


**Respuesta:** Listo. Se refactorizó solo la lógica OAuth PRE:

app/services/oauth/pre.py ahora contiene la construcción de la URL y el intercambio de tokens, con PKCE, timeout=10, manejo de errores y PreTokenExchangeError.
auth_service.py ahora delega esas operaciones a pre.py.
El resto de auth_service.py quedó igual.
No se tocaron routers, DB, DCR, CIMD ni MCPs.
Se verificó que los imports funcionen correctamente
