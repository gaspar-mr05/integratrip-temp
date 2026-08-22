CLIENT_NAME = "IntegraTrip"


def build_client_metadata(*, metadata_url: str, redirect_uris: list[str]) -> dict:
    return {
        "client_id": metadata_url,
        "client_name": CLIENT_NAME,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }
