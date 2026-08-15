import chromadb
from sentence_transformers import SentenceTransformer

_model = None
_chroma_client = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_chroma_collection():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path="./chroma_data")
    return _chroma_client.get_or_create_collection(name="medical_reports")


def add_chunks(chunks: list[str], source: str):
    """
    Embeds each chunk and stores it in ChromaDB, tagged with its source document.
    """
    model = get_embedding_model()
    collection = get_chroma_collection()

    embeddings = model.encode(chunks).tolist()
    ids = [f"{source}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)
