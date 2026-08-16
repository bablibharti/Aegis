import pytest

from app.rag.ingest import load_document


def test_load_txt_document():
    text = load_document("data/sample_reports/report1.txt")
    assert isinstance(text, str)
    assert len(text) > 0


def test_load_unsupported_file_type_raises_error(tmp_path):
    fake_file = tmp_path / "report.docx"
    fake_file.write_text("some content")

    with pytest.raises(ValueError):
        load_document(str(fake_file))


def test_load_nonexistent_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_document("data/sample_reports/does_not_exist.txt")
