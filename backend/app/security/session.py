from datetime import datetime, timedelta, timezone

from fastapi import Response, HTTPException, Cookie, status
from jose import jwt

from app.config import get_settings

SESSION_ALGORITHM = "HS256"
SESSION_COOKIE_NAME = "t1iic3103_session"
SESSION_TTL = timedelta(days=7)


def create_session_token(user_id: str) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + SESSION_TTL,
    }
    return jwt.encode(payload, settings.SESSION_SECRET_KEY, algorithm=SESSION_ALGORITHM)


def decode_session_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.SESSION_SECRET_KEY, algorithms=[SESSION_ALGORITHM])


def _cookie_attributes() -> dict:
    is_local = get_settings().ENVIRONMENT == "local"
    return {
        "httponly": True,
        "secure": not is_local,
        "samesite": "lax" if is_local else "none",
    }


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(SESSION_TTL.total_seconds()),
        **_cookie_attributes(),
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, **_cookie_attributes())


def read_session_user_id(token: str) -> str | None:
    try:
        claims = decode_session_token(token)
        return claims.get("sub")
    except Exception:
        return None


def get_current_user_id(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> str:
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un token de sesión",
        )
    user_id = read_session_user_id(session_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sesión inválido",
        )
    return user_id
