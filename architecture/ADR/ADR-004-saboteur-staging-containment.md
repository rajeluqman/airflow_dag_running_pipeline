# ADR-004 — Saboteur staging-only containment (hard boundary)

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

The live-chaos range (`@saboteur` vs `@sre-incident-commander`) injects real faults into a cloud
environment to produce MTTR-scored drills. The risk: a fault that escapes staging and reaches
prod would cause real data loss or real cost on a trial account with finite credits. Unlike a data
repo where a wrong number is a dashboard error, a prod fault here is a hard-to-reverse cloud
incident.

## Decision

Every entry in `simulation/faults/registry.py` must satisfy ALL of:

1. `environment == "staging"` — the fault targets only the staging environment.
2. `prod_credential_refs == ()` — the fault definition holds no reference to prod credentials.
3. `reversible == True` — a documented reset path exists before the fault is declared live.
4. `blast_radius` is a non-empty string — the blast radius is explicitly declared.
5. `live == False` — faults ship as `live=False`; they are not injectable until explicitly flipped
   after the Fasa 4 readiness gate.

`simulation/faults/inject.py` refuses (raises `NotImplementedError`) to inject any non-live
fault. `simulation/faults/reset.py` refuses to reset a non-reversible fault.

## Consequences

- **Positive:** A fault that passes `tests/saboteur_containment_contract.py` cannot reach prod by
  construction — it has no prod credential refs and targets only staging.
- **Positive:** The `live=False` default means no accidental injection during development.
- **Hard rule:** If `saboteur_containment_contract.py` would go red as a result of a change, the
  change does not land — fix the fault definition, never bypass the contract.
- **`@saboteur`'s mandate is scoped:** designing/running drills on staging only. Touching prod is
  outside the agent's role definition and blocked by the contract.

Full rationale: `architecture/control_plane_lab/01_OPUS_DECISIONS.md` §Saboteur containment.
