from datetime import UTC, datetime


def is_expired(expires_at: str) -> bool:
    expiration = datetime.fromisoformat(expires_at)
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=UTC)
    return expiration <= datetime.now(UTC)
