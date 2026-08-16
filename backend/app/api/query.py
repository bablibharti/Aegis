import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.blockchain.client import _get_contract
from app.cache.redis_client import get_redis_client
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    patient_id: str | None = None  # optional - if querying patient-specific data


def _cache_key(question: str) -> str:
    normalized = question.strip().lower()
    return "query_cache:" + hashlib.sha256(normalized.encode()).hexdigest()


def _check_rate_limit(
    redis_client, identifier: str, limit: int = 5, window_seconds: int = 60
) -> bool:
    key = f"rate_limit:{identifier}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window_seconds)
    return current <= limit


def _check_consent(patient_id: str, doctor_address: str) -> bool:
    """Checks on-chain whether the doctor has consent for this patient."""
    contract = _get_contract()
    return contract.functions.hasConsent(patient_id, doctor_address).call()


@router.post("/query")
def query_endpoint(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    redis_client = get_redis_client()

    if not _check_rate_limit(
        redis_client, identifier=current_user["username"], limit=5, window_seconds=60
    ):
        return {
            "answer": "Rate limit exceeded. Please wait a minute and try again.",
            "sources": [],
            "cached": False,
        }

    # If this is a patient-specific query from a doctor, verify on-chain consent first
    if request.patient_id and current_user["role"] == "doctor":
        doctor_wallet = current_user.get("wallet_address")
        if not doctor_wallet:
            raise HTTPException(
                status_code=403,
                detail="No wallet address linked to this doctor account. Cannot verify consent.",
            )

        has_consent = _check_consent(request.patient_id, doctor_wallet)
        if not has_consent:
            raise HTTPException(
                status_code=403,
                detail=f"You do not have consent to access records for patient {request.patient_id}.",
            )

    cache_key = _cache_key(request.question)

    cached = redis_client.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["cached"] = True
        return result

    chunks = retrieve_chunks(request.question, top_k=3)

    if not chunks:
        return {"answer": "No relevant documents found.", "sources": [], "cached": False}

    result = generate_answer(request.question, chunks)
    result["cached"] = False

    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result
