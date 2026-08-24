# Conversación 5

**Prompt:** Al hacer `auth/login` aparece `authenticated`, pero `auth/me` responde `"No se proporcionó un token de sesión"`.

**Respuesta:** Declarar `session_token: str | None = None` hace que FastAPI lo busque como query param, no como cookie. El token vive en la cookie de sesión, así que hay que leerlo con el helper `Cookie`:

```python
@router.get("/me")
def me(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    ...
```

El `alias` le indica a FastAPI el nombre exacto de la cookie a buscar.
