from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.api.query import router as query_router  # noqa: E402

app = FastAPI(title="Aegis AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Aegis AI backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok", "project": "aegis-professional-rebuild"}


app.include_router(query_router, tags=["rag"])
