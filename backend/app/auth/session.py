from app.cache.redis_client import get_redis_client


def blocklist_token(token: str, expires_in_seconds: int):
    """
    Adds a token to the blocklist so it can no longer be used,
    even if it hasn't naturally expired yet. Used on logout.
    """
    redis_client = get_redis_client()
    redis_client.setex(f"blocklist:{token}", expires_in_seconds, "true")


def is_token_blocklisted(token: str) -> bool:
    redis_client = get_redis_client()
    return redis_client.exists(f"blocklist:{token}") == 1
