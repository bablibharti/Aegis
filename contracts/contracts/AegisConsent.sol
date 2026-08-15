// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Aegis AI - Consent & Record Integrity Contract
/// @notice Stores record hashes (not raw data) and manages doctor consent per patient.
contract AegisConsent {
    struct RecordInfo {
        bytes32 recordHash;
        uint256 timestamp;
        address uploadedBy;
    }

    // patientId => recordId => RecordInfo
    mapping(string => mapping(string => RecordInfo)) private records;

    // patientId => doctorAddress => hasConsent
    mapping(string => mapping(address => bool)) private consents;

    event RecordHashStored(string indexed patientId, string indexed recordId, bytes32 recordHash, address uploadedBy);
    event ConsentGranted(string indexed patientId, address indexed doctor);
    event ConsentRevoked(string indexed patientId, address indexed doctor);
    event AccessLogged(string indexed recordId, address indexed accessor, uint256 timestamp);

    /// @notice Stores the hash of a medical record on-chain (not the record itself).
    function storeRecordHash(string memory patientId, string memory recordId, bytes32 recordHash) external {
        records[patientId][recordId] = RecordInfo({
            recordHash: recordHash,
            timestamp: block.timestamp,
            uploadedBy: msg.sender
        });

        emit RecordHashStored(patientId, recordId, recordHash, msg.sender);
    }

    /// @notice Returns the stored hash for a given patient's record, so it can be compared off-chain.
    function getRecordHash(string memory patientId, string memory recordId) external view returns (bytes32) {
        return records[patientId][recordId].recordHash;
    }

    /// @notice Grants a doctor consent to access a patient's records.
    function grantConsent(string memory patientId, address doctor) external {
        consents[patientId][doctor] = true;
        emit ConsentGranted(patientId, doctor);
    }

    /// @notice Revokes a doctor's consent to access a patient's records.
    function revokeConsent(string memory patientId, address doctor) external {
        consents[patientId][doctor] = false;
        emit ConsentRevoked(patientId, doctor);
    }

    /// @notice Checks whether a doctor currently has consent for a patient.
    function hasConsent(string memory patientId, address doctor) external view returns (bool) {
        return consents[patientId][doctor];
    }

    /// @notice Logs that someone accessed a record - emits an event for the audit trail.
    function logAccess(string memory recordId) external {
        emit AccessLogged(recordId, msg.sender, block.timestamp);
    }
}
