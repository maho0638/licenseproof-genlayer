# LicenseProof validation and evidence levels

Test the entire state machine: publish, grant, accept, report, review, appeal, resolve and revoke; assert no unauthorized transitions.

Security regression topics:
- Frozen license terms and scope hashes; cross-grant isolation; SHA-256 readback.
- Role spoofing, unknown addresses, zero address, malformed IDs and control characters.
- Duplicate grants, reports, reviews, appeals and revocations.
- Revocation safety: cannot create new reports but cannot erase earlier evidence.
- Unknown/malicious JSON from the model must normalize to INSUFFICIENT.
- Validator reruns on exact normalized verdict; disagreement rejects.
- Prompt-injection in licensee-supplied evidence remains text data.

**Verification tiers**:
1. Syntax and isolated checks are developer tests.
2. GenVM lint, typecheck and schema are compatibility checks.
3. Official Direct Mode runs a simulated state flow with mocked LLM responses, not real network consensus.
4. Real Studionet proof requires a separately authorized deployment, signed transactions, receipt inspection and RPC readback.
5. Independent security audit is not performed.

Never publish credentials, main-wallet keys or fabricated chain receipts. Treat original and appeal decisions as claim classifications rather than findings of fact.
