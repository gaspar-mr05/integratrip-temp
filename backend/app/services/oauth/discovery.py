import logging
import re
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

DISCOVERY_REQUEST_TIMEOUT = 10
REQUIRED_AS_METADATA_FIELDS = (
    "issuer",
    "authorization_endpoint",
    "token_endpoint",
    "jwks_uri",
)
BEARER_PARAM_RE = re.compile(
    r'(?:^|,\s*)([A-Za-z_][\w-]*)=(?:"([^"]*)"|([^,\s]+))'
)


class OAuthDiscoveryError(Exception):
    pass


def _parse_bearer_challenge(header: str | None) -> dict[str, str]:
    if header is None:
        raise OAuthDiscoveryError("El MCP no devolvió WWW-Authenticate")

    scheme, _, params = header.partition(" ")
    if scheme.lower() != "bearer" or not params:
        raise OAuthDiscoveryError("El WWW-Authenticate del MCP no es Bearer")

    return {
        match.group(1): match.group(2) if match.group(2) is not None else match.group(3)
        for match in BEARER_PARAM_RE.finditer(params)
    }


def _discover_resource_metadata_url(resource_url: str) -> str:
    try:
        response = requests.post(resource_url, timeout=DISCOVERY_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Falló discovery inicial contra el recurso MCP")
        raise OAuthDiscoveryError("No se pudo contactar al recurso MCP") from exc

    if response.status_code != 401:
        raise OAuthDiscoveryError("El recurso MCP no respondió 401 para iniciar OAuth")

    params = _parse_bearer_challenge(response.headers.get("www-authenticate"))
    resource_metadata_url = params.get("resource_metadata")
    if not resource_metadata_url:
        raise OAuthDiscoveryError("El WWW-Authenticate no incluyó resource_metadata")
    return resource_metadata_url


def _get_json_metadata(url: str, description: str) -> dict:
    try:
        response = requests.get(url, timeout=DISCOVERY_REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.exception("Falló obteniendo %s", description)
        raise OAuthDiscoveryError(f"No se pudo obtener {description}") from exc

    if response.status_code != 200:
        raise OAuthDiscoveryError(f"El servidor rechazó {description}")

    try:
        metadata = response.json()
    except ValueError as exc:
        raise OAuthDiscoveryError(f"{description} no es JSON válido") from exc

    if not isinstance(metadata, dict):
        raise OAuthDiscoveryError(f"{description} no tiene formato de objeto JSON")
    return metadata


def _authorization_server_metadata_urls(issuer: str) -> list[str]:
    parsed = urlparse(issuer)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise OAuthDiscoveryError("El issuer descubierto no es una URL válida")

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rstrip("/")
    issuer_url = issuer.rstrip("/")

    return [
        f"{base_url}/.well-known/oauth-authorization-server{path}",
        f"{issuer_url}/.well-known/openid-configuration",
        f"{issuer_url}/.well-known/oauth-authorization-server",
    ]


def _discover_authorization_server_metadata(issuer: str) -> dict:
    last_error: OAuthDiscoveryError | None = None

    for metadata_url in _authorization_server_metadata_urls(issuer):
        try:
            metadata = _get_json_metadata(metadata_url, "metadata del AS")
        except OAuthDiscoveryError as exc:
            last_error = exc
            continue

        if metadata.get("issuer") == issuer:
            return metadata

        last_error = OAuthDiscoveryError(
            "La metadata del AS no coincide con el issuer descubierto"
        )

    raise last_error or OAuthDiscoveryError("No se pudo descubrir metadata del AS")


def _require_string(metadata: dict, key: str, description: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value:
        raise OAuthDiscoveryError(f"{description} no incluyó {key}")
    return value


def _validate_as_metadata(metadata: dict) -> None:
    for field in REQUIRED_AS_METADATA_FIELDS:
        _require_string(metadata, field, "La metadata del AS")

    if "code" not in metadata.get("response_types_supported", []):
        raise OAuthDiscoveryError("El AS no soporta response_type code")

    if "authorization_code" not in metadata.get("grant_types_supported", []):
        raise OAuthDiscoveryError("El AS no soporta authorization_code")

    if "S256" not in metadata.get("code_challenge_methods_supported", []):
        raise OAuthDiscoveryError("El AS no soporta PKCE S256")

    if metadata.get("resource_indicators_supported") is not True:
        raise OAuthDiscoveryError("El AS no declara resource indicators")


def discover_mcp_oauth_metadata(resource_url: str) -> dict:
    resource_metadata_url = _discover_resource_metadata_url(resource_url)
    resource_metadata = _get_json_metadata(
        resource_metadata_url,
        "metadata del recurso protegido",
    )

    resource = _require_string(
        resource_metadata,
        "resource",
        "La metadata del recurso protegido",
    )
    authorization_servers = resource_metadata.get("authorization_servers")
    if not isinstance(authorization_servers, list) or not authorization_servers:
        raise OAuthDiscoveryError(
            "La metadata del recurso protegido no incluyó authorization_servers"
        )

    issuer = authorization_servers[0]
    if not isinstance(issuer, str) or not issuer:
        raise OAuthDiscoveryError("authorization_servers no incluyó un issuer válido")

    as_metadata = _discover_authorization_server_metadata(issuer)
    _validate_as_metadata(as_metadata)

    scopes = resource_metadata.get("scopes_supported")
    scope = "mcp:tools"
    if isinstance(scopes, list) and scopes and isinstance(scopes[0], str):
        scope = scopes[0]

    registration_endpoint = as_metadata.get("registration_endpoint")
    if registration_endpoint is not None and not isinstance(registration_endpoint, str):
        raise OAuthDiscoveryError("registration_endpoint no tiene formato válido")

    return {
        "resource": resource,
        "scope": scope,
        "issuer": issuer,
        "authorization_endpoint": as_metadata["authorization_endpoint"],
        "token_endpoint": as_metadata["token_endpoint"],
        "jwks_uri": as_metadata["jwks_uri"],
        "registration_endpoint": registration_endpoint,
        "client_id_metadata_document_supported": as_metadata.get(
            "client_id_metadata_document_supported"
        )
        is True,
        "grant_types_supported": as_metadata.get("grant_types_supported", []),
        "token_endpoint_auth_methods_supported": as_metadata.get(
            "token_endpoint_auth_methods_supported", []
        ),
    }
