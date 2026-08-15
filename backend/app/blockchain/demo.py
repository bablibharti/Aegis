"""
Tamper-detection demo for Aegis AI.

Demonstrates: storing a medical record's hash on-chain, then showing
that any modification to the record is detectable via hash mismatch,
while the actual record content never touches the blockchain.
"""

from dotenv import load_dotenv

load_dotenv()

from app.blockchain.client import store_record_hash, verify_record_hash  # noqa: E402


def run_demo():
    patient_id = "demo_patient_001"
    record_id = "demo_record_001"
    original_content = "Patient presented with mild fever and elevated blood pressure."

    print("=" * 60)
    print("AEGIS AI - TAMPER DETECTION DEMO")
    print("=" * 60)

    print(f"\nOriginal record:\n  '{original_content}'")

    print("\nStoring hash of this record on-chain (Polygon Amoy)...")
    tx_hash = store_record_hash(patient_id, record_id, original_content)
    print(f"  Transaction hash: {tx_hash}")
    print(f"  View on explorer: https://amoy.polygonscan.com/tx/{tx_hash}")

    print("\n--- Scenario 1: Verifying untouched record ---")
    is_valid = verify_record_hash(patient_id, record_id, original_content)
    print(f"  Record matches on-chain hash: {is_valid}")
    assert is_valid, "Expected untouched record to verify successfully!"

    print("\n--- Scenario 2: Verifying a TAMPERED record ---")
    tampered_content = original_content + " Follow-up not required."
    print(f"  Tampered record:\n  '{tampered_content}'")
    is_valid_after_tamper = verify_record_hash(patient_id, record_id, tampered_content)
    print(f"  Record matches on-chain hash: {is_valid_after_tamper}")
    assert not is_valid_after_tamper, "Expected tampered record to FAIL verification!"

    print("\n" + "=" * 60)
    print("RESULT: Tampering was successfully detected via hash mismatch.")
    print("The original record content was never stored on-chain -")
    print("only its cryptographic hash, preserving patient privacy")
    print("while guaranteeing data integrity.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
