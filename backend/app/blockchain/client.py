import hashlib
import json
import os
from pathlib import Path

from web3 import Web3

_w3 = None
_contract = None


def _get_web3():
    global _w3
    if _w3 is None:
        rpc_url = os.environ.get("AMOY_RPC_URL")
        _w3 = Web3(Web3.HTTPProvider(rpc_url))
    return _w3


def _get_contract():
    global _contract
    if _contract is None:
        w3 = _get_web3()
        abi_path = Path(__file__).parent / "AegisConsent.json"
        with open(abi_path) as f:
            artifact = json.load(f)
        contract_address = os.environ.get("CONTRACT_ADDRESS")
        _contract = w3.eth.contract(address=contract_address, abi=artifact["abi"])
    return _contract


def compute_record_hash(content: str) -> bytes:
    """Computes a SHA-256 hash of record content."""
    return hashlib.sha256(content.encode()).digest()


def store_record_hash(patient_id: str, record_id: str, content: str) -> str:
    """
    Hashes the record content and stores the hash on-chain.
    Returns the transaction hash.
    """
    w3 = _get_web3()
    contract = _get_contract()
    private_key = os.environ.get("PRIVATE_KEY")
    account = w3.eth.account.from_key(private_key)

    record_hash = compute_record_hash(content)

    tx = contract.functions.storeRecordHash(patient_id, record_id, record_hash).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        }
    )

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_hash.hex()


def verify_record_hash(patient_id: str, record_id: str, content: str) -> bool:
    """
    Recomputes the hash of the given content and compares it
    against what's stored on-chain.
    """
    contract = _get_contract()
    stored_hash = contract.functions.getRecordHash(patient_id, record_id).call()
    current_hash = compute_record_hash(content)

    return stored_hash == current_hash
