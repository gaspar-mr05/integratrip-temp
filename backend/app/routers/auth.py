from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse

from app.db.users import UserUpsertError
from app.security.session import clear_session_cookie, get_current_user_id, set_session_cookie
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


@router.get("/login")
def login():
    try:
        url = start_login_flow()
    except LoginFlowError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return RedirectResponse(url)


@router.get("/callback")
def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    if error is not None:
        raise HTTPException(status_code=400, detail=error_description or error)

    if code is None or state is None:
        raise HTTPException(status_code=400, detail="Faltan los parámetros code y state")

    try:
        code_verifier = consume_code_verifier(state)
    except InvalidLoginStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        session_token = complete_login(code, code_verifier)
    except TokenExchangeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UserUpsertError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response = JSONResponse({"status": "authenticated"})
    set_session_cookie(response, session_token)
    return response


@router.get("/me")
def me(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}


@router.get("/logout")
def logout():
    response = RedirectResponse(get_settings().FRONTEND_URL)
    clear_session_cookie(response)
    return response