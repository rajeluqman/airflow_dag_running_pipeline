# ADR-006 — Env-promotion gate (staging drill green before prod)

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

The repo's prod environment (MWAA, real cloud jobs, real data) represents the highest-blast-radius
target. Any change that reaches prod must have been validated somewhere that looks like prod but
isn't. The alternative — direct prod edits "just this once" — is how trial credits and data get
lost, and it bypasses the MTTR training loop that is the whole point of the chaos range.

## Decision

Production promotion is gated: a change may reach prod ONLY AFTER a staging drill for that change
has completed green AND the MTTR has been recorded in `simulation/MTTR_SCORECARD.md`.

`tests/env_promotion_contract.py` enforces this mechanically:
- If `infra/terraform/prod/` does not exist (Fasa 1–2 invariant): the contract passes trivially —
  there is no prod environment to protect yet, so no promotion gate can be tripped.
- If `infra/terraform/prod/` exists (Fasa 3+): every file in that directory must appear in
  `simulation/MTTR_SCORECARD.md` — proof that a staging drill was recorded before any prod
  resource was provisioned.

There is no "just this once" direct prod edit. The gate is the path.

## Consequences

- **Positive:** Prod is structurally un-reachable until at least one staged drill has been run and
  recorded. This is a teaching-lab invariant: MTTR is a prerequisite for prod access.
- **Fasa 1–2 behavior:** The contract passes trivially because `infra/terraform/prod/` does not
  exist. This is correct — there is no prod to protect yet.
- **Fasa 3+ behavior:** `@platform-architect` must approve any new prod resource; `@sre-incident-
  commander` must record an MTTR for a staging analog before the resource is provisioned.
- **Limitation:** The contract checks file-name presence in the scorecard, not drill quality. A
  dummy scorecard entry would pass. The enforcement relies on the honor system and Opus review of
  the PR.
