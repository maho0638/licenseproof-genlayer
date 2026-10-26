# LicenseProof — GenLayer Intelligent Contract for license claims

LicenseProof provides an immutable license-and-usage workflow with **recipient-bound grants**, explicit acceptance, a consensus-assisted evaluation of self-reported use and one appeal.

## Why GenLayer?

Ordinary deterministic contracts can store approvals and hashes, but deciding whether a natural-language use declaration is compatible with license terms is a semantic judgment. This contract uses `gl.nondet.exec_prompt` with `gl.vm.run_nondet_unsafe`; validators re-evaluate the **exact normalized decision** rather than comparing free-form prose.

Possible verdicts:

- `CONSISTENT`: the **claimed use** appears explicitly within immutable terms and granted scope.
- `CONFLICT`: the claimed use clearly breaches them.
- `INSUFFICIENT`: evidence or rules do not support a reliable classification, or model output is malformed.

**The model does NOT authenticate evidence, detect real-world usage, establish legal enforceability, issue licenses on behalf of real rights holders, or guarantee correct decisions.**

## Workflow and permissions

1. **Issuer**: `publish_license(license_id, asset_name, terms)` freezes terms permanently.
2. **Issuer**: `issue_grant(grant_id, license_id, licensee_hex, scope)` binds the permission to a specific recipient and stores terms/scope SHA-256.
3. **Recipient**: `accept_grant(grant_id)` explicitly acknowledges the grant.
4. **Recipient**: `file_usage(grant_id, declaration, evidence)` records one self-reported usage statement and evidence.
5. **Issuer**: `evaluate_usage(grant_id)` performs a validator-consensus classification and stores the immutable original.
6. **Recipient**: `file_appeal(grant_id, additional_evidence)` files one extra evidence statement.
7. **Issuer**: `resolve_appeal(grant_id)` performs a second consensus classification; original verdict remains unchanged.
8. **Issuer**: `revoke_grant(grant_id)` blocks future acceptance/usage filings. Previously submitted reports and valid appeals remain auditable and resolvable; revocation does **not** rewrite history or enforce anything off-chain.

Views: `get_license`, `get_grant`, `get_report`, `get_review(grant_id, appeal)`.

## Security boundaries

- Strict issuer/recipient authorization on all writes.
- Unique IDs, one-time actions and bounded UTF-8 inputs.
- Immutable natural-language license terms, per-grant scope and SHA-256 commitments.
- Unknown/invalid AI output defaults to `INSUFFICIENT`; validators reject mismatched normalized decisions.
- User-supplied text is XML-escaped and marked untrusted in the model prompt.
- No tokens, royalties, fund custody, external contracts or automated legal conclusions.
- **Liveness is not guaranteed:** issuer may refuse to run or resolve reviews.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m pytest tests/direct -q
genvm-lint check contracts/license_proof.py
genvm-lint typecheck contracts/license_proof.py
genvm-lint schema contracts/license_proof.py
```

Check the **GitHub Actions history** for actual results. Green Direct Mode checks use mock LLM outputs; they are not evidence of real Studionet deployment. No mainnet, signed transactions, independent security audit, authenticated content ownership or guaranteed license compliance is claimed.
