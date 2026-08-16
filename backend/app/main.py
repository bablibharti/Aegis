from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.auth import router as auth_router  # noqa: E402
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


app.include_router(auth_router, tags=["auth"])
app.include_router(query_router, tags=["rag"])
