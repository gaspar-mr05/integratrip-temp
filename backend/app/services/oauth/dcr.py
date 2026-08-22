

import logging

import requests

logger = logging.getLogger(__name__)

REGISTER_REQUEST_TIMEOUT = 10


class DcrRegistrationError(Exception):
    pass


def register_client(*, registration_endpoint: str, redirect_uris: list[str], client_name: str) -> dict:
    data = {
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_post",
    }
    try:
        response = requests.post(registration_endpoint, json=data, timeout=REGISTER_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Fallo la conexión con el registration_endpoint del AS")
        raise DcrRegistrationError("No se pudo contactar al servidor de autorización") from exc

    if response.status_code not in (200, 201):
        logger.error(
            "El AS rechazó el registro dinámico: %s %s",
            response.status_code,
            response.text,
        )
        raise DcrRegistrationError("El servidor de autorización rechazó el registro del cliente")

    registration = response.json()
    if not registration.get("client_id"):
        logger.error("El AS registró el cliente sin devolver client_id: %s", registration)
        raise DcrRegistrationError("El servidor de autorización no devolvió un client_id")

    return registration
