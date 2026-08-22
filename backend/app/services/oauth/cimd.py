import logging
import requests

logger = logging.getLogger(__name__)

TOKEN_REQUEST_TIMEOUT = 10


class CimdTokenExchangeError(Exception):
    pass


def cimd_exchange_code_for_tokens(
    *,
    token_endpoint: str,
    client_id: str,
    redirect_uri: str,
    code: str,
    code_verifier: str,
) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    try:
        response = requests.post(token_endpoint, data=data, timeout=TOKEN_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Fallo la conexión con el token endpoint del AS")
        raise CimdTokenExchangeError("No se pudo contactar al servidor de autorización") from exc

    if response.status_code != 200:
        logger.error(
            "El AS rechazó el intercambio de código: %s %s",
            response.status_code,
            response.text,
        )
        raise CimdTokenExchangeError("El servidor de autorización rechazó el código")

    return response.json()