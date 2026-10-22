"""Direct-mode tests for ReleaseEvidenceAttestor.

All external data is mocked.  These are not live GitHub, Studio, or network
tests; they verify contract state, error paths, and the custom validator.
"""

import json

import pytest


OWNER = "acme"
REPOSITORY = "release-demo"
TAG = "v1.0.0"
EVIDENCE_ISSUE = 42
CHALLENGE_ISSUE = 43
RUBRIC = "Release notes must describe the attestor and issue evidence must confirm delivery."
RELEASE_URL = "https://api.github.com/repos/acme/release-demo/releases/tags/v1.0.0"
EVIDENCE_URL = "https://api.github.com/repos/acme/release-demo/issues/42"
CHALLENGE_URL = "https://api.github.com/repos/acme/release-demo/issues/43"


@pytest.fixture
def attestor(direct_vm, direct_deploy):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True
    # genlayer-test 0.29.2 follows GitHub's "latest" GenVM release by default.
    # That archived release no longer exposes the asset name the test loader
    # expects. Pin a still-published runner matching the contract's SDK hash.
    return direct_deploy("contracts/release_evidence_attestor.py", sdk_version="v0.2.16")


def release_payload(notes="Includes the documented attestor contract."):
    return json.dumps({"id": 1001, "tag_name": TAG, "name": "Version 1.0.0", "body": notes})


def issue_payload(number, title, body):
    return json.dumps({"number": number, "title": title, "body": body, "state": "closed"})


def mock_assessment(vm, decision="SATISFIED", notes="Includes the documented attestor contract."):
    vm.mock_web(r"https://api\.github\.com/repos/acme/release-demo/releases/tags/v1\.0\.0$", {"status": 200, "body": release_payload(notes)})
    vm.mock_web(r"https://api\.github\.com/repos/acme/release-demo/issues/42$", {"status": 200, "body": issue_payload(42, "Release evidence", "The release contains the requested feature.")})
    vm.mock_llm(r"(?s).*bounded public release evidence.*", json.dumps({"decision": decision, "rationale": "Mocked assessment rationale."}))


def test_creation_has_no_user_controlled_source_url(attestor, direct_vm):
    claim_id = attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, RUBRIC)
    assert claim_id == "0"
    assert attestor.get_evidence_urls(claim_id) == {"release": RELEASE_URL, "evidence_issue": EVIDENCE_URL, "challenge_issue": ""}
    with direct_vm.expect_revert("unsupported character"):
        attestor.create_claim(OWNER, "release/demo", TAG, EVIDENCE_ISSUE, RUBRIC)
    with direct_vm.expect_revert("20 to 700"):
        attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, "short")
    with direct_vm.expect_revert("positive GitHub issue"):
        attestor.create_claim(OWNER, REPOSITORY, TAG, 0, RUBRIC)


def test_assessment_stores_only_stable_decision_gates(attestor, direct_vm):
    claim_id = attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, RUBRIC)
    mock_assessment(direct_vm)
    attestor.assess_claim(claim_id)
    claim = attestor.get_claim(claim_id)
    assert (claim["status"], claim["decision"], claim["release_id"]) == ("ASSESSED", "SATISFIED", "1001")
    assert len(claim["release_digest"]) == 64
    assert len(claim["evidence_digest"]) == 64
    assert direct_vm.run_validator(index=0) is True


def test_validator_rejects_changed_release_evidence(attestor, direct_vm):
    claim_id = attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, RUBRIC)
    mock_assessment(direct_vm)
    attestor.assess_claim(claim_id)
    direct_vm.clear_mocks()
    mock_assessment(direct_vm, notes="The release notes were materially changed after assessment.")
    assert direct_vm.run_validator(index=0) is False


def test_single_challenge_can_uphold_or_overturn_the_assessment(attestor, direct_vm):
    claim_id = attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, RUBRIC)
    mock_assessment(direct_vm)
    attestor.assess_claim(claim_id)
    attestor.challenge_claim(claim_id, CHALLENGE_ISSUE)
    direct_vm.mock_web(r"https://api\.github\.com/repos/acme/release-demo/issues/43$", {"status": 200, "body": issue_payload(43, "Counter evidence", "No contradiction was found.")})
    direct_vm.mock_llm(r"(?s).*bounded GitHub counter-evidence issue.*", json.dumps({"decision": "UPHOLD", "rationale": "No concrete contradiction."}))
    attestor.resolve_challenge(claim_id)
    claim = attestor.get_claim(claim_id)
    assert (claim["status"], claim["decision"], claim["challenge_decision"]) == ("FINAL", "SATISFIED", "UPHOLD")
    with direct_vm.expect_revert("no pending challenge"):
        attestor.resolve_challenge(claim_id)


def test_uncontested_finalization_is_creator_only(attestor, direct_vm, direct_bob):
    claim_id = attestor.create_claim(OWNER, REPOSITORY, TAG, EVIDENCE_ISSUE, RUBRIC)
    mock_assessment(direct_vm, decision="REJECTED")
    attestor.assess_claim(claim_id)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("Only the claim creator"):
            attestor.finalize_uncontested(claim_id)
    attestor.finalize_uncontested(claim_id)
    assert attestor.get_claim(claim_id)["status"] == "FINAL"
