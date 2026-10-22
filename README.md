# GenLayer Release Evidence Attestor

An experimental GenLayer Intelligent Contract primitive for attesting whether a
public GitHub release satisfies a short, explicit delivery rubric.

> **Status — pre-deployment prototype.** The contract has local logic tests and
> mocked GenLayer Direct Mode tests. It has not been deployed, audited, accepted
> by the GenLayer Portal, or used to make legal, financial, employment, or other
> high-stakes decisions.

## Why this primitive is narrow

This is intentionally **not** a generic AI task grader. Each claim is limited to:

- a GitHub owner and repository;
- one release tag;
- one GitHub issue containing the delivery evidence; and
- a bounded, human-written acceptance rubric.

The contract constructs its own GitHub REST API URLs. Callers cannot supply an
arbitrary URL, credential, host, or prompt target. This makes the primitive
reusable for open-source delivery review while keeping its evidence boundary
small and inspectable.

## Contract lifecycle

~~~text
OPEN
  | assess_claim()
  v
ASSESSED -- challenge_claim(issue) --> CHALLENGED
  |                                      | resolve_challenge()
  | finalize_uncontested()               v
  +-----------------------------------> FINAL
~~~

1. create_claim stores a bounded release claim.
2. assess_claim fetches the matching GitHub Release and evidence Issue.
3. Each GenLayer node makes its own non-deterministic requests and constrained
   LLM assessment. The result is SATISFIED, REJECTED, or INCONCLUSIVE.
4. Before finalization, anyone may attach one different GitHub issue as
   counter-evidence. resolve_challenge returns UPHOLD, OVERTURN, or
   INCONCLUSIVE, then finalizes the claim.
5. If no counter-evidence is attached, only the claim creator can call
   finalize_uncontested.

The current prototype uses an explicit one-challenge state transition rather
than a timestamp-based challenge window. A production deployment should define
its governance and timing policy before relying on finality.

## Consensus design

ReleaseEvidenceAttestor uses custom GenLayer leader and validator functions,
not a format-only comparison:

- both the leader and each validator independently fetch GitHub Release and
  Issue API objects;
- the model sees bounded release/issue text and a fixed JSON decision schema;
- validators re-run that work and compare the decision plus the release ID,
  tag, issue number, and SHA-256 digests of the evidence fields;
- free-form rationale is stored for review but deliberately excluded from the
  equivalence check because different models may word it differently.

If the GitHub evidence changes between the leader and a validator, the digest
comparison fails rather than silently accepting stale or divergent evidence.

## Repository layout

~~~text
contracts/release_evidence_attestor.py   standalone Intelligent Contract
tests/unit/test_release_logic.py         no-SDK state and validation tests
tests/direct/test_release_evidence_attestor.py
                                         Direct Mode and mock consensus tests
docs/design.md                           evidence boundary and trust model
docs/verification.md                    completed verification only
requirements.txt                         pinned test-tool versions
~~~

The older Evidence Court and frontend prototype files are retained locally for
history. They are not part of this release-attestation primitive and will not
be included in the public submission source.

## Local verification

The project is developed under WSL. Direct Mode requires Python 3.12 or later.

~~~bash
cd /mnt/d/Backup/Documents/测试网脚本/genlayer-evidence-court
uv venv --python 3.12 /tmp/genlayer-release-attestor-venv
uv pip install --python /tmp/genlayer-release-attestor-venv/bin/python -r requirements.txt
python3 tests/unit/test_release_logic.py
/tmp/genlayer-release-attestor-venv/bin/python -m pytest tests/direct/test_release_evidence_attestor.py -v
~~~

The Direct Mode fixture currently pins a still-published historical GenVM
runner, v0.2.16, compatible with the contract SDK hash. See
docs/verification.md for the precise limitation: the test tool automatic
latest-runner download currently returns HTTP 404.

## Operational limits

- GitHub rate limits, deleted releases/issues, API changes, or dynamic evidence
  can produce a user-visible error or validator disagreement.
- The contract does not authenticate GitHub authors, prove that a release is
  safe, or audit code.
- A passing result says only that the configured public evidence met the
  configured rubric under GenLayer consensus; it is not independent proof of
  quality or security.
- Never use this prototype for high-stakes decisions without a dedicated
  security review, threat model, governance policy, and live-network testing.

## Next verification boundary

Before a Portal contribution is submitted, remaining work is to run the
contract in GenLayer Studio or an approved test environment, verify one actual
multi-validator transaction against a real public release, record the deployed
address and transaction evidence, and update this repository with only those
observed results.

## License

MIT. See LICENSE.
