# Conversación 3

**Prompt:** No me lee las variables de entorno en el archivo actual. ¿Qué puedo hacer?

**Respuesta:** Las variables estaban en `backend/.env`, pero nadie las cargaba: un `.env` no se inyecta solo en Python.

Se creó `app/config.py` con una clase `Settings(BaseSettings)` de `pydantic-settings` que declara y tipa cada variable. Si falta una obligatoria, la app falla al arrancar con un mensaje claro. `auth.py` ahora usa `settings.AS_AUTHORIZATION_ENDPOINT` en vez de nombres sueltos.

Pendiente: pasar los parámetros de la URL por `urlencode` y persistir `state` y `code_verifier` antes de redirigir.
