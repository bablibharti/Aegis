import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("AegisConsentModule", (m) => {
  const aegisConsent = m.contract("AegisConsent");

  return { aegisConsent };
});
