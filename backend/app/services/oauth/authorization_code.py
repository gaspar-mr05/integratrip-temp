import logging
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

TOKEN_REQUEST_TIMEOUT = 10


class OAuthTokenExchangeError(Exception):
    pass


def build_authorization_url(
    *,
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
    resource: str,
    scope: str = "openid",
) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "resource": resource,
    }
    return f"{authorization_endpoint}?{urlencode(params)}"


def exchange_code_for_tokens(
    *,
    token_endpoint: str,
    client_id: str,
    redirect_uri: str,
    code: str,
    code_verifier: str,
    client_secret: str | None = None,
) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret

    try:
        response = requests.post(token_endpoint, data=data, timeout=TOKEN_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Fallo la conexión con el token endpoint del AS")
        raise OAuthTokenExchangeError("No se pudo contactar al servidor de autorización") from exc

    if response.status_code != 200:
        logger.error(
            "El AS rechazó el intercambio de código: %s %s",
            response.status_code,
            response.text,
        )
        raise OAuthTokenExchangeError("El servidor de autorización rechazó el código")

    return response.json()
