import { describe, it } from "node:test";
import { expect } from "chai";
import { network } from "hardhat";


describe("AegisConsent", async function () {
  const { viem } = await network.connect();

  async function deployContract() {
    const contract = await viem.deployContract("AegisConsent");
    const [owner, doctor, otherAccount] = await viem.getWalletClients();
    return { contract, owner, doctor, otherAccount };
  }

  describe("Record Hash Storage", function () {
    it("should store and retrieve a record hash", async function () {
      const { contract } = await deployContract();

      const patientId = "patient001";
      const recordId = "record001";
      const hash = "0x" + "a".repeat(64);

      await contract.write.storeRecordHash([
        patientId,
        recordId,
        hash as `0x${string}`,
      ]);
      const storedHash = await contract.read.getRecordHash([
        patientId,
        recordId,
      ]);

      expect(storedHash.toLowerCase()).to.equal(hash);
    });

    it("should return zero hash for non-existent record", async function () {
      const { contract } = await deployContract();
      const storedHash = await contract.read.getRecordHash([
        "unknown",
        "unknown",
      ]);
      expect(storedHash).to.equal("0x" + "0".repeat(64));
    });
  });

  describe("Consent Management", function () {
    it("should grant consent to a doctor", async function () {
      const { contract, doctor } = await deployContract();
      const patientId = "patient001";

      await contract.write.grantConsent([patientId, doctor.account.address]);
      const consentStatus = await contract.read.hasConsent([
        patientId,
        doctor.account.address,
      ]);

      expect(consentStatus).to.equal(true);
    });

    it("should revoke consent from a doctor", async function () {
      const { contract, doctor } = await deployContract();
      const patientId = "patient001";

      await contract.write.grantConsent([patientId, doctor.account.address]);
      await contract.write.revokeConsent([patientId, doctor.account.address]);
      const consentStatus = await contract.read.hasConsent([
        patientId,
        doctor.account.address,
      ]);

      expect(consentStatus).to.equal(false);
    });

    it("should return false for a doctor with no consent", async function () {
      const { contract, otherAccount } = await deployContract();
      const consentStatus = await contract.read.hasConsent([
        "patient001",
        otherAccount.account.address,
      ]);
      expect(consentStatus).to.equal(false);
    });
  });

  describe("Access Logging", function () {
    it("should log access without reverting", async function () {
      const { contract } = await deployContract();
      await contract.write.logAccess(["record001"]);
      // If this doesn't throw, the call succeeded
    });
  });
});
