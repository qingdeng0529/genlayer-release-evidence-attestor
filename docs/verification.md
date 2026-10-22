# Verification record

This record lists observed checks only. It does not imply deployment,
multi-validator live consensus, audit, Portal approval, rewards, or production
readiness.

## 2026-10-22 — Release Evidence Attestor

Environment:

- WSL distribution/user: Ubuntu-22.04 / qingdeng.
- Project path: /mnt/d/Backup/Documents/测试网脚本/genlayer-evidence-court.
- Isolated test runtime: Python 3.12.13 in /tmp/genlayer-release-attestor-venv.
- Tool versions: genlayer-test 0.29.2, genvm-linter 0.11.0, and pytest 9.1.1.

Completed:

- Python syntax compilation of the new contract and its test modules completed.
- GenVM linter AST safety check passed all 3 checks for
  contracts/release_evidence_attestor.py.
- Three local state/validation tests passed using a deliberately fake GenLayer
  API. They do not test GenVM, network access, or consensus.
- Five official GenLayer Direct Mode tests passed with mocked GitHub Release,
  Issue, and LLM responses:
  - restricted identifier-only claim creation;
  - stable decision/evidence gate storage;
  - validator disagreement when release evidence changes;
  - bounded counter-evidence challenge lifecycle; and
  - creator-only uncontested finalization.
- Direct Mode ran with strict mocks and pickling checks enabled.

Direct Mode runner limitation:

- genlayer-test 0.29.2 defaults to downloading genvm-universal.tar.xz from the
  latest GenVM release. On 2026-10-22 that request targeted v0.3.0-rc7 and
  returned HTTP 404 before contract code ran.
- The tests explicitly pin the still-published historical v0.2.16 runner,
  which loaded the contract and produced the five passing Direct Mode results.
- This is a testing-tool/release-asset compatibility issue. It does not
  establish compatibility with a current Studio, testnet, or validator fleet.

Not completed:

- Current GenVM lint semantic validation against an available latest runner.
- GenLayer Studio/localnet integration test.
- Testnet deployment or any wallet signature.
- Live GitHub API assessment with real GenLayer validators.
- Audit, Portal review, acceptance, or reward claim.

## Historical prototype

The earlier generic Evidence Court prototype and its frontend were explored
locally before the scope was narrowed. They are not part of the Release Evidence
Attestor source set and are not a basis for any verification claim above.
