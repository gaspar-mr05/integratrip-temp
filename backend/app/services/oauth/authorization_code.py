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
    scope: str = "mcp:tools",
    prompt: str | None = None,
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
    if prompt is not None:
        params["prompt"] = prompt

    return f"{authorization_endpoint}?{urlencode(params)}"


def _post_token_request(token_endpoint: str, data: dict, grant_description: str) -> dict:
    try:
        response = requests.post(token_endpoint, data=data, timeout=TOKEN_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Falló la conexión con el token endpoint del AS")
        raise OAuthTokenExchangeError("No se pudo contactar al servidor de autorización") from exc

    if response.status_code != 200:
        logger.error(
            "El AS rechazó el %s: %s %s",
            grant_description,
            response.status_code,
            response.text,
        )
        raise OAuthTokenExchangeError(
            f"El servidor de autorización rechazó el {grant_description}"
        )

    return response.json()


def exchange_code_for_tokens(
    *,
    token_endpoint: str,
    client_id: str,
    redirect_uri: str,
    code: str,
    code_verifier: str,
    resource: str,
    client_secret: str | None = None,
) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
        "resource": resource,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret

    return _post_token_request(token_endpoint, data, "intercambio de código")


def refresh_access_token(
    *,
    token_endpoint: str,
    client_id: str,
    refresh_token: str,
    resource: str,
    client_secret: str | None = None,
) -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "resource": resource,
    }
    if client_secret is not None:
        data["client_secret"] = client_secret

    return _post_token_request(token_endpoint, data, "refresh de token")
