from jose import jwt


def read_unverified_access_token_claims(access_token: str) -> dict:
    return jwt.get_unverified_claims(access_token)
