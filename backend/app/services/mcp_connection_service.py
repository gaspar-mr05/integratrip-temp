from app.db.mcp_connections import upsert_mcp_connection
from app.db.mcp_servers import get_mcp_server_by_name, update_mcp_server_credentials
from app.db.oauth_mcp_state import consume_mcp_state, insert_mcp_state
from app.security.pkce import (
    create_code_verifier,
    generate_state,
    transform_code_verifier_to_code_challenge,
)
from app.services.oauth.dcr import DcrRegistrationError, register_client
from app.services.oauth.pre import (
    PreTokenExchangeError,
    build_authorization_url,
    exchange_code_for_tokens,
)
from app.services.oauth.cimd import (
    CimdTokenExchangeError,
    cimd_exchange_code_for_tokens,
)
from app.services.oauth.state_expiry import is_state_expired
from app.config import get_settings

settings = get_settings()


class ConnectionFlowError(Exception):
    pass


class InvalidConnectionStateError(Exception):
    pass


def _get_mcp_server(server_name: str) -> dict:
    mcp_server = get_mcp_server_by_name(server_name)
    if mcp_server is None:
        raise ConnectionFlowError(f"No existe el servidor MCP '{server_name}'")
    return mcp_server


def _resolve_redirect_uri(mcp_server: dict) -> str:
    """Primera URL del array en producción, última en local."""
    if settings.ENVIRONMENT == "production":
        return mcp_server["redirect_uris"][0]
    return mcp_server["redirect_uris"][-1]


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
    mcp_server = _get_mcp_server(server_name)
    if mcp_server["client_id"] is None:
        mcp_server = _register_dynamic_client(mcp_server)

    code_verifier = create_code_verifier()
    state = generate_state()

    if not insert_mcp_state(user_id, mcp_server["id"], state, code_verifier):
        raise ConnectionFlowError("No se pudo guardar el state del flujo de conexión")

    return build_authorization_url(
        authorization_endpoint=mcp_server["authorization_endpoint"],
        client_id=mcp_server["client_id"],
        redirect_uri=_resolve_redirect_uri(mcp_server),
        state=state,
        code_challenge=transform_code_verifier_to_code_challenge(code_verifier),
        resource=mcp_server["mcp_url"],
    )


def _consume_connection_state(state: str, mcp_server_id: str) -> dict:
    mcp_state = consume_mcp_state(state)
    if mcp_state is None:
        raise InvalidConnectionStateError("El state no existe o ya fue utilizado")

    if is_state_expired(mcp_state["expires_at"]):
        raise InvalidConnectionStateError("El flujo de conexión expiró, intenta nuevamente")

    if mcp_state["mcp_server_id"] != mcp_server_id:
        raise InvalidConnectionStateError("El state no corresponde a este servidor MCP")

    return mcp_state


def complete_mcp_connection_flow(server_name: str, state: str, code: str) -> dict:
    mcp_server = _get_mcp_server(server_name)
    mcp_state = _consume_connection_state(state, mcp_server["id"])
    redirect_uri = _resolve_redirect_uri(mcp_server)

    try:
        if mcp_server["auth_type"] in ("PRE", "DCR"):
            tokens = exchange_code_for_tokens(
                token_endpoint=mcp_server["token_endpoint"],
                client_id=mcp_server["client_id"],
                client_secret=mcp_server["client_secret_enc"],
                redirect_uri=redirect_uri,
                code=code,
                code_verifier=mcp_state["code_verifier"],
            )
        elif mcp_server["auth_type"] == "CIMD":
            tokens = cimd_exchange_code_for_tokens(
                token_endpoint=mcp_server["token_endpoint"],
                client_id=mcp_server["client_id"],
                redirect_uri=redirect_uri,
                code=code,
                code_verifier=mcp_state["code_verifier"],
            )
        else:
            raise ConnectionFlowError(f"Tipo de auth no soportado: {mcp_server['auth_type']}")
    except (PreTokenExchangeError, CimdTokenExchangeError) as exc:
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