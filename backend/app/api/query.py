import hashlib
import json

from fastapi import APIRouter
from pydantic import BaseModel

from app.cache.redis_client import get_redis_client
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


def _cache_key(question: str) -> str:
    """Creates a consistent cache key from the question text."""
    normalized = question.strip().lower()
    return "query_cache:" + hashlib.sha256(normalized.encode()).hexdigest()


def _check_rate_limit(
    redis_client, identifier: str, limit: int = 5, window_seconds: int = 60
) -> bool:
    """
    Returns True if request is allowed, False if rate limit exceeded.
    Simple fixed-window counter per identifier (e.g. IP or user id).
    """
    key = f"rate_limit:{identifier}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window_seconds)
    return current <= limit


@router.post("/query")
def query_endpoint(request: QueryRequest):
    redis_client = get_redis_client()

    # Rate limit check first
    if not _check_rate_limit(redis_client, identifier="demo_user", limit=5, window_seconds=60):
        return {
            "answer": "Rate limit exceeded. Please wait a minute and try again.",
            "sources": [],
            "cached": False,
        }

    cache_key = _cache_key(request.question)

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["cached"] = True
        return result

    # Not cached - run the real RAG pipeline
    chunks = retrieve_chunks(request.question, top_k=3)

    if not chunks:
        return {"answer": "No relevant documents found.", "sources": [], "cached": False}

    result = generate_answer(request.question, chunks)
    result["cached"] = False

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result
