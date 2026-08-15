import os

import redis

_client = None


def get_redis_client():
    global _client
    if _client is None:
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        _client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    return _client
