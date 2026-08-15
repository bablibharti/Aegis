import os

from groq import Groq

_client = None


def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


def generate_answer(query: str, chunks: list[dict]) -> dict:
    """
    Sends the query + retrieved chunks to Groq, asking it to answer
    ONLY using the given context, and to cite which source it used.
    """
    client = get_groq_client()

    context = "\n\n".join(f"[Source: {c['source']}]\n{c['text']}" for c in chunks)

    prompt = f"""You are a medical assistant. Answer the question using ONLY the context below.
If the answer isn't in the context, say you don't have enough information.
Always mention which source(s) you used.

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content
    sources = list({c["source"] for c in chunks})

    return {"answer": answer, "sources": sources}
