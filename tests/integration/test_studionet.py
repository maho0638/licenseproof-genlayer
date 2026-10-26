"""Live Studionet-only test: signs TEST network transactions. NEVER run automatically.

Required: two separate SDK test accounts. This is NOT authentication of
off-chain licensing or an independent audit. Run by explicit workflow_dispatch
only after a human confirms network writes and deployment are authorized.
"""
import hashlib
import json
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

TERMS = "One educational video with creator credit permitted. Direct asset resale prohibited."
SCOPE = "One credited educational video, non-exclusive."
EVIDENCE = "Licensee reports that one educational video credits the creator; URL not verified."
SUPPLEMENT = "Licensee reports that the attribution appears in the closing credits."


def record(value):
    return json.loads(str(value))


@pytest.mark.integration
def test_licenseproof_studionet_two_parties(default_account, accounts):
    licensee = next((x for x in accounts
        if str(x.address).lower() != str(default_account.address).lower()), None)
    assert licensee is not None, "Two distinct test accounts required"

    factory = get_contract_factory("LicenseProof")
    contract = factory.deploy(account=default_account, consensus_max_rotations=4)
    recipient_contract = contract.connect(licensee)
    print("LICENSEPROOF_CONTRACT=" + str(contract.address), flush=True)

    tx = contract.publish_license(args=["LIVE-L1", "Licensed media demo", TERMS]).transact(
        wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("PUBLISH_LICENSE_TX=" + str(tx.get("hash", "")), flush=True)
    license_record = record(contract.get_license(args=["LIVE-L1"]).call())
    assert license_record["terms_sha256"] == hashlib.sha256(TERMS.encode()).hexdigest()
    assert license_record["issuer"].lower() == str(default_account.address).lower()

    tx = contract.issue_grant(args=["LIVE-G1", "LIVE-L1", str(licensee.address), SCOPE]).transact(
        wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("ISSUE_GRANT_TX=" + str(tx.get("hash", "")), flush=True)
    grant = record(contract.get_grant(args=["LIVE-G1"]).call())
    assert grant["terms_sha256"] == license_record["terms_sha256"]
    assert grant["scope_sha256"] == hashlib.sha256(SCOPE.encode()).hexdigest()
    assert grant["licensee"].lower() == str(licensee.address).lower()

    tx = recipient_contract.accept_grant(args=["LIVE-G1"]).transact(
        wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("ACCEPT_GRANT_TX=" + str(tx.get("hash", "")), flush=True)
    assert record(contract.get_grant(args=["LIVE-G1"]).call())["accepted"] is True

    tx = recipient_contract.file_usage(args=[
        "LIVE-G1", "I used the asset in one educational video with attribution.", EVIDENCE
    ]).transact(wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("FILE_USAGE_TX=" + str(tx.get("hash", "")), flush=True)
    report = record(contract.get_report(args=["LIVE-G1"]).call())
    assert report["evidence_sha256"] == hashlib.sha256(EVIDENCE.encode()).hexdigest()

    tx = contract.evaluate_usage(args=["LIVE-G1"]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=100)
    assert tx_execution_succeeded(tx)
    print("INITIAL_CONSENSUS_TX=" + str(tx.get("hash", "")), flush=True)
    first = record(contract.get_review(args=["LIVE-G1", False]).call())
    assert first["verdict"] in {"CONSISTENT", "CONFLICT", "INSUFFICIENT"}
    assert first["round_number"] == 0
    assert first["terms_sha256"] == license_record["terms_sha256"]
    assert first["evidence_sha256"] == report["evidence_sha256"]

    tx = recipient_contract.file_appeal(args=["LIVE-G1", SUPPLEMENT]).transact(
        wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("FILE_APPEAL_TX=" + str(tx.get("hash", "")), flush=True)

    tx = contract.resolve_appeal(args=["LIVE-G1"]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=100)
    assert tx_execution_succeeded(tx)
    print("APPEAL_CONSENSUS_TX=" + str(tx.get("hash", "")), flush=True)
    assert record(contract.get_review(args=["LIVE-G1", False]).call()) == first
    second = record(contract.get_review(args=["LIVE-G1", True]).call())
    assert second["round_number"] == 1
    assert second["verdict"] in {"CONSISTENT", "CONFLICT", "INSUFFICIENT"}
    assert second["evidence_sha256"] == hashlib.sha256(
        (EVIDENCE + "\nADDITIONAL EVIDENCE:\n" + SUPPLEMENT).encode()).hexdigest()

    tx = contract.revoke_grant(args=["LIVE-G1"]).transact(
        wait_interval=10000, wait_retries=70)
    assert tx_execution_succeeded(tx)
    print("REVOKE_GRANT_TX=" + str(tx.get("hash", "")), flush=True)
    assert record(contract.get_grant(args=["LIVE-G1"]).call())["revoked"] is True
    assert record(contract.get_review(args=["LIVE-G1", False]).call()) == first
    print("LICENSEPROOF_NETWORK_READBACK_OK=true", flush=True)
