import pytest

from app.rag.chunker import chunk_text
from app.rag.retriever import retrieve_chunks
from app.rag.vectorstore import add_chunks, get_chroma_collection


@pytest.fixture(autouse=True)
def clean_test_collection():
    """Ensures each test starts with a clean collection."""
    collection = get_chroma_collection()
    # Remove any existing test data before each test
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
    yield


def test_retrieve_returns_relevant_chunk():
    text = "The patient reported severe headaches and dizziness during the visit."
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    add_chunks(chunks, source="test_doc")

    results = retrieve_chunks("What symptoms did the patient have?", top_k=1)

    assert len(results) > 0
    assert "source" in results[0]
    assert results[0]["source"] == "test_doc"


def test_retrieve_returns_empty_for_no_data():
    results = retrieve_chunks("Some random query with no matching data", top_k=3)
    assert isinstance(results, list)
