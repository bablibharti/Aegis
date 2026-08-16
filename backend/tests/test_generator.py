from unittest.mock import MagicMock, patch

from app.rag.generator import generate_answer


@patch("app.rag.generator.get_groq_client")
def test_generate_answer_returns_grounded_response(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "The patient had a fever."
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    chunks = [{"text": "Patient had fever.", "source": "report1"}]
    result = generate_answer("What symptoms?", chunks)

    assert result["answer"] == "The patient had a fever."
    assert result["sources"] == ["report1"]


@patch("app.rag.generator.get_groq_client")
def test_generate_answer_deduplicates_sources(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Some answer."
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client

    chunks = [
        {"text": "chunk 1", "source": "report1"},
        {"text": "chunk 2", "source": "report1"},
    ]
    result = generate_answer("test question", chunks)

    assert result["sources"] == ["report1"]
