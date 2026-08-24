"""Conectar un usuario con un servidor MCP: flujo OAuth y tokens vigentes."""

from app.config import get_settings
from app.db.mcp_connections import get_mcp_connection, upsert_mcp_connection
from app.db.mcp_servers import get_mcp_server_by_name, update_mcp_server_credentials
from app.db.oauth_mcp_state import consume_mcp_state, insert_mcp_state
from app.security.pkce import (
    create_code_verifier,
    generate_state,
    transform_code_verifier_to_code_challenge,
)
from app.services.oauth.authorization_code import (
    OAuthTokenExchangeError,
    build_authorization_url,
    exchange_code_for_tokens,
    refresh_access_token,
)
from app.services.oauth.dcr import DcrRegistrationError, register_client
from app.services.oauth.expiration import is_expired

SUPPORTED_AUTH_TYPES = ("PRE", "DCR", "CIMD")
PUBLIC_CLIENT_AUTH_TYPES = ("CIMD",)
MCP_SCOPE = "mcp:tools"


class ConnectionFlowError(Exception):
    pass


class InvalidConnectionStateError(Exception):
    pass


class McpServerNotFoundError(Exception):
    pass


class McpNotConnectedError(Exception):
    pass


def resolve_mcp_server(server_name: str) -> dict:
    mcp_server = get_mcp_server_by_name(server_name)
    if mcp_server is None:
        raise McpServerNotFoundError(f"No existe el servidor MCP '{server_name}'")
    if mcp_server["auth_type"] not in SUPPORTED_AUTH_TYPES:
        raise ConnectionFlowError(f"Tipo de auth no soportado: {mcp_server['auth_type']}")
    return mcp_server


def mcp_endpoint(mcp_server: dict) -> str:
    return f"{mcp_server['mcp_url']}/mcp"


def _redirect_uri(mcp_server: dict) -> str:
    if get_settings().ENVIRONMENT == "production":
        return mcp_server["redirect_uris"][0]
    return mcp_server["redirect_uris"][-1]


def _client_secret(mcp_server: dict) -> str | None:
    """Los clientes públicos (CIMD) se autentican sin secret."""
    if mcp_server["auth_type"] in PUBLIC_CLIENT_AUTH_TYPES:
        return None
    return mcp_server["client_secret_enc"]


def _register_dynamic_client(mcp_server: dict) -> dict:
    registration_endpoint = mcp_server["registration_endpoint"]
    if not registration_endpoint:
        raise ConnectionFlowError(
            f"El servidor MCP '{mcp_server['name']}' no tiene client_id ni registration_endpoint"
        )

    try:
        registration = register_client(
            registration_endpoint=registration_endpoint,
            redirect_uris=mcp_server["redirect_uris"],
            client_name=f"IntegraTrip - {mcp_server['name']}",
        )
    except DcrRegistrationError as exc:
        raise ConnectionFlowError(str(exc)) from exc

    updated = update_mcp_server_credentials(
        mcp_server["id"],
        registration["client_id"],
        registration.get("client_secret"),
    )
    if updated is None:
        raise ConnectionFlowError("No se pudo guardar el cliente registrado dinámicamente")
    return updated


def start_mcp_connection_flow(user_id: str, server_name: str) -> str:
    mcp_server = resolve_mcp_server(server_name)
    if mcp_server["auth_type"] == "DCR" and not mcp_server["client_id"]:
        mcp_server = _register_dynamic_client(mcp_server)

    if not mcp_server["client_id"]:
        raise ConnectionFlowError(
            f"El servidor MCP '{mcp_server['name']}' no tiene client_id configurado"
        )

    code_verifier = create_code_verifier()
    state = generate_state()

    if not insert_mcp_state(user_id, mcp_server["id"], state, code_verifier):
        raise ConnectionFlowError("No se pudo guardar el state del flujo de conexión")

    return build_authorization_url(
        authorization_endpoint=mcp_server["authorization_endpoint"],
        client_id=mcp_server["client_id"],
        redirect_uri=_redirect_uri(mcp_server),
        state=state,
        code_challenge=transform_code_verifier_to_code_challenge(code_verifier),
        resource=mcp_endpoint(mcp_server),
        scope=MCP_SCOPE,
    )


def _consume_connection_state(state: str, mcp_server_id: str) -> dict:
    mcp_state = consume_mcp_state(state)
    if mcp_state is None:
        raise InvalidConnectionStateError("El state no existe o ya fue utilizado")

    if is_expired(mcp_state["expires_at"]):
        raise InvalidConnectionStateError("El flujo de conexión expiró, intenta nuevamente")

    if mcp_state["mcp_server_id"] != mcp_server_id:
        raise InvalidConnectionStateError("El state no corresponde a este servidor MCP")

    return mcp_state


def complete_mcp_connection_flow(server_name: str, state: str, code: str) -> dict:
    mcp_server = resolve_mcp_server(server_name)
    mcp_state = _consume_connection_state(state, mcp_server["id"])

    try:
        tokens = exchange_code_for_tokens(
            token_endpoint=mcp_server["token_endpoint"],
            client_id=mcp_server["client_id"],
            client_secret=_client_secret(mcp_server),
            redirect_uri=_redirect_uri(mcp_server),
            code=code,
            code_verifier=mcp_state["code_verifier"],
            resource=mcp_endpoint(mcp_server),
        )
    except OAuthTokenExchangeError as exc:
        raise ConnectionFlowError(str(exc)) from exc

    access_token = tokens.get("access_token")
    if access_token is None:
        raise ConnectionFlowError("El servidor de autorización no devolvió un access_token")

    connection = upsert_mcp_connection(
        user_id=mcp_state["user_id"],
        mcp_server_id=mcp_state["mcp_server_id"],
        access_token=access_token,
        refresh_token=tokens.get("refresh_token"),
        expires_in=tokens.get("expires_in"),
        scope=tokens.get("scope"),
    )
    if connection is None:
        raise ConnectionFlowError("No se pudo guardar la conexión con el servidor MCP")
    return connection


def _refresh_connection(mcp_server: dict, user_id: str, refresh_token: str) -> str:
    try:
        tokens = refresh_access_token(
            token_endpoint=mcp_server["token_endpoint"],
            client_id=mcp_server["client_id"],
            client_secret=_client_secret(mcp_server),
            refresh_token=refresh_token,
            resource=mcp_endpoint(mcp_server),
        )
    except OAuthTokenExchangeError as exc:
        raise ConnectionFlowError(str(exc)) from exc

    access_token = tokens.get("access_token")
    if access_token is None:
        raise ConnectionFlowError(
            "El servidor de autorización no devolvió un access_token al refrescar"
        )

    upsert_mcp_connection(
        user_id=user_id,
        mcp_server_id=mcp_server["id"],
        access_token=access_token,
        # Si el AS no rota el refresh_token, conservamos el que ya teníamos.
        refresh_token=tokens.get("refresh_token") or refresh_token,
        expires_in=tokens.get("expires_in"),
        scope=tokens.get("scope"),
    )
    return access_token


def get_valid_access_token(user_id: str, mcp_server: dict) -> str:
    """Devuelve un access_token vigente, refrescándolo si expiró."""
    mcp_connection = get_mcp_connection(user_id, mcp_server["id"])
    if mcp_connection is None:
        raise McpNotConnectedError(f"No has conectado '{mcp_server['name']}' todavía")

    expires_at = mcp_connection["expires_at"]
    if expires_at is None or not is_expired(expires_at):
        return mcp_connection["access_token_enc"]

    refresh_token = mcp_connection["refresh_token_enc"]
    if refresh_token is None:
        raise McpNotConnectedError(
            f"El access_token de '{mcp_server['name']}' expiró y no hay refresh_token"
        )

    return _refresh_connection(mcp_server, user_id, refresh_token)
