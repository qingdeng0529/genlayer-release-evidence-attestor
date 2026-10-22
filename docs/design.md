# Release Evidence Attestor: design and evidence boundary

## Purpose

Open-source maintainers, grant programs, and reviewers sometimes need a
repeatable way to answer a narrow question: does one named public GitHub release
have public issue evidence that meets a stated delivery rubric?

The contract records that question and runs an AI-assisted assessment under
GenLayer consensus. It does not determine whether software is secure, useful,
original, lawful, or generally complete.

## Allowed evidence

The contract accepts identifiers, not URLs:

| Input | Constraint | Derived source |
| --- | --- | --- |
| Owner and repository | ASCII letters, digits, dot, underscore, hyphen; 1–100 characters each | GitHub repository API |
| Release tag | Same conservative path-segment policy | Release by tag API |
| Evidence issue number | Positive bounded integer | Issue API |
| Rubric | 20–700 characters | Stored on-chain |
| Optional challenge issue | One different positive issue number | Issue API |

There is no caller-controlled hostname, URL scheme, HTTP method, request body,
credential, or prompt source.

## Stable evidence gate

Each non-deterministic evaluation extracts only:

- release ID and tag;
- requested issue number;
- SHA-256 digest of the release name/notes; and
- SHA-256 digest of the issue title/body/state.

The raw text is used transiently in the bounded LLM prompt. It is not stored in
the result object. A validator independently repeats the fetch and semantic
assessment. It must agree with the leader on every evidence gate and decision.
It may word the rationale differently; rationale therefore has no consensus
weight.

## Decision semantics

Initial assessment:

- SATISFIED: both public sources explicitly support every requirement of the rubric.
- REJECTED: the sources explicitly establish that the rubric is not met.
- INCONCLUSIVE: evidence is missing, ambiguous, malformed, or the model does
  not provide a valid decision.

One separate issue may be attached as a challenge:

- OVERTURN: it gives concrete public evidence that the release fails the rubric.
- UPHOLD: it does not.
- INCONCLUSIVE: it cannot be determined from the bounded evidence.

OVERTURN changes the final decision to REJECTED. An upheld initial SATISFIED
result remains satisfied. All other challenge outcomes end as INCONCLUSIVE.

## Threat model and non-goals

This prototype reduces rather than eliminates risks:

- A repository owner can publish misleading public material.
- GitHub API availability and rate limits are outside the contract control.
- A release or issue can change after assessment; the stored digest is an audit
  marker, not a permanent content archive.
- LLM assessment is only used on bounded evidence and is checked through
  validator re-execution. It is not autonomous proof.
- The contract is non-custodial and contains no payment, token, voting, or
  access-control system beyond creator-only uncontested finalization.

For real governance, add a review period, authorized-reviewer rules, a
content-archival strategy, and an independent security review.
