import { network } from "hardhat";

async function main() {
  const { viem } = await network.connect({ network: "amoy" });

  const contractAddress = "0xB70B4659ea1802BaD78fE59BAE7CEf14b94B002f";
  const doctorWallet = "0x6a6365F5dae1b75d1d2131f9026aa0053A7D7c94"; // apna MetaMask address yaha daalo

  const contract = await viem.getContractAt("AegisConsent", contractAddress);
  const publicClient = await viem.getPublicClient();

  console.log("Granting consent...");
  const txHash = await contract.write.grantConsent([
    "patient001",
    doctorWallet,
  ]);
  console.log("Transaction hash:", txHash);

  console.log("Waiting for confirmation...");
  await publicClient.waitForTransactionReceipt({ hash: txHash });

  const hasConsent = await contract.read.hasConsent([
    "patient001",
    doctorWallet,
  ]);
  console.log("Has consent:", hasConsent);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
