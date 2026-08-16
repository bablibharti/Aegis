from app.blockchain.client import compute_record_hash


def test_compute_record_hash_is_deterministic():
    content = "Patient has mild fever."
    hash1 = compute_record_hash(content)
    hash2 = compute_record_hash(content)
    assert hash1 == hash2


def test_compute_record_hash_differs_for_different_content():
    hash1 = compute_record_hash("Patient has mild fever.")
    hash2 = compute_record_hash("Patient has severe fever.")
    assert hash1 != hash2


def test_compute_record_hash_returns_32_bytes():
    result = compute_record_hash("any content")
    assert len(result) == 32  # SHA-256 always produces 32 bytes
