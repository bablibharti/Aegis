from app.rag.vectorstore import get_chroma_collection, get_embedding_model


def retrieve_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    Embeds the query and returns the top_k most similar chunks from ChromaDB,
    along with their source metadata.
    """
    model = get_embedding_model()
    collection = get_chroma_collection()

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    retrieved = []
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        retrieved.append({"text": doc, "source": metadata["source"]})

    return retrieved
