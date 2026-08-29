import logging

from app.config import get_settings
from app.db.oauth_login_state import consume_login_state, insert_login_state
from app.db.users import upsert_user
from app.security.pkce import (
    create_code_verifier,
    generate_state,
    transform_code_verifier_to_code_challenge,
)
from app.security.session import create_session_token
from app.security.access_token import read_unverified_access_token_claims
from app.services.oauth import authorization_code
from app.services.oauth.expiration import is_expired

logger = logging.getLogger(__name__)


class LoginFlowError(Exception):
    pass


class InvalidLoginStateError(Exception):
    pass


class TokenExchangeError(Exception):
    pass


def start_login_flow() -> str:
    settings = get_settings()

    code_verifier = create_code_verifier()
    state = generate_state()

    if not insert_login_state(state, code_verifier):
        raise LoginFlowError("No se pudo guardar el state del flujo de login")

    return authorization_code.build_authorization_url(
        authorization_endpoint=settings.AS_AUTHORIZATION_ENDPOINT,
        client_id=settings.LOGIN_CLIENT_ID,
        redirect_uri=settings.login_redirect_uri,
        state=state,
        code_challenge=transform_code_verifier_to_code_challenge(code_verifier),
        resource=settings.BACKEND_URL,
    )


def consume_code_verifier(state: str) -> str:
    login_state = consume_login_state(state)
    if login_state is None:
        raise InvalidLoginStateError("El state no existe o ya fue utilizado")

    if is_expired(login_state["expires_at"]):
        raise InvalidLoginStateError("El flujo de login expiró, intenta nuevamente")

    return login_state["code_verifier"]


def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    settings = get_settings()
    try:
        return authorization_code.exchange_code_for_tokens(
            token_endpoint=settings.AS_TOKEN_ENDPOINT,
            client_id=settings.LOGIN_CLIENT_ID,
            client_secret=settings.LOGIN_CLIENT_SECRET,
            redirect_uri=settings.login_redirect_uri,
            code=code,
            code_verifier=code_verifier,
            resource=settings.BACKEND_URL,
        )
    except authorization_code.OAuthTokenExchangeError as exc:
        raise TokenExchangeError(str(exc)) from exc


def complete_login(code: str, code_verifier: str) -> str:
    tokens = exchange_code_for_tokens(code, code_verifier)

    access_token = tokens.get("access_token")
    if access_token is None:
        logger.error("El AS no devolvió access_token: %s", sorted(tokens))
        raise TokenExchangeError("El servidor de autorización no devolvió un access_token")

    claims = read_unverified_access_token_claims(access_token)
    user = upsert_user(as_subject=claims["sub"], email=claims.get("email"))
    return create_session_token(user["id"])
