# Conversación 4

Prompt: Soluciona los detalles pendientes de la ruta /auth/callback.

Respuesta: Los problemas eran que no se validaba el state (podía ser None o estar expirado y el flujo seguía igual), y que leer y borrar la fila eran dos operaciones separadas.

En db/oauth_login_state.py, consume_login_state(state) hace un solo delete que devuelve la fila borrada o None, así leer y consumir es atómico.

En services/auth_service.py, consume_code_verifier(state) valida que la fila exista y no haya expirado, o levanta InvalidLoginStateError.

En routers/auth.py, /callback acepta code, state, error y error_description como opcionales, y responde 400 en cada caso inválido.
