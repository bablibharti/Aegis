from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.generator import generate_answer
from app.rag.retriever import retrieve_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query_endpoint(request: QueryRequest):
    chunks = retrieve_chunks(request.question, top_k=3)

    if not chunks:
        return {"answer": "No relevant documents found.", "sources": []}

    result = generate_answer(request.question, chunks)
    return result
