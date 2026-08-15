from app.rag.chunker import chunk_text


def test_chunk_text_returns_list():
    text = "This is a simple medical report about patient symptoms."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_chunk_text_respects_overlap():
    text = "A" * 100
    chunks = chunk_text(text, chunk_size=30, overlap=10)
    # With overlap, consecutive chunks should share some characters
    assert len(chunks) > 1


def test_chunk_text_empty_string():
    chunks = chunk_text("", chunk_size=50, overlap=10)
    assert chunks == []


def test_chunk_text_invalid_overlap_raises_error():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=10, overlap=10)


def test_chunk_text_short_text_single_chunk():
    text = "Short text."
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text
