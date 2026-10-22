# Portal submission draft — do not submit before live evidence exists

## Contribution type

Developer / Intelligent Contracts.

## Suggested title

Release Evidence Attestor — bounded GitHub release evidence consensus primitive

## Suggested description

Release Evidence Attestor is a standalone GenLayer Intelligent Contract for a
narrow open-source review workflow. A requester records one GitHub repository,
release tag, evidence issue, and an explicit acceptance rubric. The contract
constructs its own GitHub API URLs, preventing caller-controlled external
sources. During assessment, the leader and validators independently fetch the
release and issue, run a constrained JSON LLM assessment, and compare the
decision plus stable evidence gates: release ID, tag, issue number, and
SHA-256 digests of release and issue evidence. One separate issue can provide
counter-evidence before finalization. The repository includes identifier and
state validation tests, mock web/LLM Direct Mode tests, and a validator
disagreement test for changed evidence.

## Evidence links after source upload

1. Repository root:
   https://github.com/qinxin001/genlayer-release-evidence-attestor
2. Contract source:
   https://github.com/qinxin001/genlayer-release-evidence-attestor/blob/main/contracts/release_evidence_attestor.py
3. Direct Mode tests:
   https://github.com/qinxin001/genlayer-release-evidence-attestor/blob/main/tests/direct/test_release_evidence_attestor.py
4. Design and verification record:
   https://github.com/qinxin001/genlayer-release-evidence-attestor/tree/main/docs

## Required updates before actual Portal submission

- Upload the listed source files and verify their GitHub URLs load publicly.
- Allow the GitHub Actions workflow to run and record its observed result.
- Deploy to GenLayer Studio or another approved test environment using a
  dedicated test wallet.
- Run one real release assessment with actual validators.
- Add the deployed address, transaction link, and observed result to the
  verification record.
- Do not claim an audit, acceptance, production readiness, or reward unless it
  has actually happened.
