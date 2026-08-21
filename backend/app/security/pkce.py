import base64
import hashlib
import secrets


def create_code_verifier() -> str:
    return secrets.token_urlsafe(32)


def transform_code_verifier_to_code_challenge(code_verifier: str) -> str:
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode("utf-8")


def generate_state() -> str:
    return secrets.token_urlsafe(32)
