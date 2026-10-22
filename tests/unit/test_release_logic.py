"""Fast local checks using a deliberately tiny fake GenLayer API.

These tests prove ordinary Python state rules only.  The direct tests exercise
the real GenLayer test SDK, mocked web/LLM calls, and validator callbacks.
"""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class FakeAddress:
    as_hex = "0x" + "1" * 40


class FakeContract:
    def __new__(cls):
        instance = super().__new__(cls)
        instance.claims = {}
        return instance


class FakeResponse:
    def __init__(self, payload):
        self.status_code = 200
        self.body = payload.encode("utf-8")


def load_contract():
    identity = lambda value: value
    public = types.SimpleNamespace(write=identity, view=identity)
    releases = {
        "id": 1001,
        "tag_name": "v1.0.0",
        "name": "Version 1.0.0",
        "body": "Includes the documented attestor contract.",
    }
    issues = {
        "/issues/42": {"number": 42, "title": "Release evidence", "body": "The release contains the requested feature.", "state": "closed"},
        "/issues/43": {"number": 43, "title": "Counter evidence", "body": "No contradiction was found.", "state": "closed"},
    }

    def get(url):
        import json
        if "/releases/tags/" in url:
            return FakeResponse(json.dumps(releases))
        for suffix, payload in issues.items():
            if url.endswith(suffix):
                return FakeResponse(json.dumps(payload))
        return FakeResponse("{}")

    def prompt(prompt_text, response_format):
        if "counter-evidence" in prompt_text.lower():
            return {"decision": "UPHOLD", "rationale": "The challenge does not contradict the release."}
        return {"decision": "SATISFIED", "rationale": "The evidence addresses the rubric."}

    class Return:
        def __init__(self, calldata):
            self.calldata = calldata

    fake = types.ModuleType("genlayer")
    fake.allow_storage = identity
    fake.Address = FakeAddress
    fake.u256 = int
    fake.TreeMap = dict
    fake.gl = types.SimpleNamespace(
        Contract=FakeContract,
        public=public,
        nondet=types.SimpleNamespace(web=types.SimpleNamespace(get=get), exec_prompt=prompt),
        vm=types.SimpleNamespace(UserError=Exception, Return=Return, run_nondet_unsafe=lambda leader, validator: leader()),
        message=types.SimpleNamespace(sender_address=FakeAddress()),
    )
    path = Path(__file__).resolve().parents[2] / "contracts" / "release_evidence_attestor.py"
    spec = importlib.util.spec_from_file_location("release_attestor_local", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"genlayer": fake, spec.name: module}):
        spec.loader.exec_module(module)
    return module


class ReleaseAttestorLogicTests(unittest.TestCase):
    def setUp(self):
        self.module = load_contract()
        self.contract = self.module.ReleaseEvidenceAttestor()
        self.rubric = "Release notes must describe the attestor and issue evidence must confirm delivery."

    def create(self):
        return self.contract.create_claim("acme", "release-demo", "v1.0.0", 42, self.rubric)

    def test_create_and_restrict_inputs(self):
        self.assertEqual(self.create(), "0")
        self.assertEqual(self.contract.get_claim_count(), 1)
        with self.assertRaisesRegex(Exception, "unsupported character"):
            self.contract.create_claim("acme", "release/demo", "v1.0.0", 42, self.rubric)
        with self.assertRaisesRegex(Exception, "20 to 700"):
            self.contract.create_claim("acme", "release-demo", "v1.0.0", 42, "too short")
        with self.assertRaisesRegex(Exception, "positive GitHub issue"):
            self.contract.create_claim("acme", "release-demo", "v1.0.0", 0, self.rubric)

    def test_assess_and_finalize(self):
        claim_id = self.create()
        self.contract.assess_claim(claim_id)
        claim = self.contract.get_claim(claim_id)
        self.assertEqual((claim["status"], claim["decision"]), ("ASSESSED", "SATISFIED"))
        self.assertEqual(len(claim["release_digest"]), 64)
        self.contract.finalize_uncontested(claim_id)
        self.assertEqual(self.contract.get_claim(claim_id)["status"], "FINAL")

    def test_one_issue_challenge_is_bounded(self):
        claim_id = self.create()
        self.contract.assess_claim(claim_id)
        with self.assertRaisesRegex(Exception, "must differ"):
            self.contract.challenge_claim(claim_id, 42)
        self.contract.challenge_claim(claim_id, 43)
        self.contract.resolve_challenge(claim_id)
        claim = self.contract.get_claim(claim_id)
        self.assertEqual((claim["status"], claim["decision"], claim["challenge_decision"]), ("FINAL", "SATISFIED", "UPHOLD"))


if __name__ == "__main__":
    unittest.main()
