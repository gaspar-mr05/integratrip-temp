from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.db.users import UserUpsertError
from app.security.session import (
    SESSION_COOKIE_NAME,
    clear_session_cookie,
    get_current_user_id,
    get_optional_session_user_id,
    set_session_cookie,
)
from app.services.auth_service import (
    InvalidLoginStateError,
    LoginFlowError,
    TokenExchangeError,
    complete_login,
    consume_code_verifier,
    start_login_flow,
)

from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, headers={"Cache-Control": "no-store"})


@router.get("/login")
def login():
    try:
        url = start_login_flow()
    except LoginFlowError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _redirect(url)


@router.get("/callback")
def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    existing_session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    if error is not None:
        raise HTTPException(status_code=400, detail=error_description or error)

    if code is None or state is None:
        raise HTTPException(status_code=400, detail="Faltan los parámetros code y state")

    try:
        code_verifier = consume_code_verifier(state)
    except InvalidLoginStateError as exc:
        # El AS puede repetir el callback después de que el primer request ya
        # consumió el state. Si ese request creó una sesión válida, no dejamos
        # al usuario detenido en el error del replay.
        if get_optional_session_user_id(existing_session_token) is not None:
            return _redirect(get_settings().FRONTEND_URL)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        session_token = complete_login(code, code_verifier)
    except TokenExchangeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UserUpsertError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response = _redirect(get_settings().FRONTEND_URL)
    set_session_cookie(response, session_token)
    return response


@router.get("/me")
def me(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}


@router.get("/logout")
def logout():
    response = _redirect(get_settings().FRONTEND_URL)
    clear_session_cookie(response)
    return response
