# Conversación 7

Prompt: Extrae solo la lógica OAuth PRE genérica de auth_service.py hacia app/services/oauth/pre.py.

En pre.py crea build_authorization_url, que recibe authorization_endpoint, client_id, redirect_uri, state, code_challenge, resource y scope="openid"; y exchange_code_for_tokens, que recibe token_endpoint, client_id, client_secret, redirect_uri, code y code_verifier. Ambas con keyword-only arguments.

La función de token debe mantener exactamente el comportamiento actual: timeout=10, manejo de requests.RequestException, error si el status no es 200 y los mismos logs. Crea una excepción propia PreTokenExchangeError.

Luego modifica auth_service.py para usar estas funciones en start_login_flow y exchange_code_for_tokens. No modifiques routers, DB, DCR ni CIMD.

Respuesta: app/services/oauth/pre.py quedó con la construcción de la URL y el intercambio de tokens, incluyendo PKCE, timeout=10, manejo de errores y PreTokenExchangeError. auth_service.py delega esas dos operaciones a pre.py y el resto quedó igual.

No se tocaron routers, DB, DCR, CIMD ni MCPs. Se verificó que los imports funcionen.
