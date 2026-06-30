# Isolation Contract — Chaos-Range Containment Rules

> Companion to `tests/saboteur_containment_contract.py` (mechanical enforcement) and
> `simulation/check_isolation.py` (health check). This document is the human-readable statement
> of the isolation invariants. If this doc and the contract script ever disagree, the script is
> the ground truth — update this doc to match, not the other way around.

---

## The invariants

Every fault in `simulation/faults/registry.py` must satisfy ALL of the following before it can
be declared live (`live=True`) or injected:

1. **Staging only.** `environment == "staging"`. No fault targets prod, dev, or any
   non-staging environment.

2. **No prod credential refs.** `prod_credential_refs == ()`. A fault definition must not hold
   any reference to production credentials, connection strings, or account identifiers. Even a
   comment in a fault file naming a prod resource is a containment failure.

3. **Reversible.** `reversible == True`. A reset path must exist and be documented in
   `simulation/faults/reset.py` before the fault ships. An irreversible fault is not a drill —
   it is an incident.

4. **Declared blast radius.** `blast_radius` is a non-empty string describing exactly which
   staging resources the fault affects. "Everything" is not an acceptable blast-radius declaration.

5. **Budget ceiling.** `budget_ceiling_usd > 0`. The maximum expected cloud cost of one drill
   run is declared upfront. The auto-teardown fires if MTTR exceeds this ceiling.

6. **Auto-teardown.** `auto_teardown` is a non-empty string describing the teardown command or
   mechanism. This is not optional even if the fault is "cheap" — the ceiling and teardown pair
   is what makes cost safety structural rather than procedural.

---

## What @saboteur may and may not do

**May:**
- Design fault definitions targeting staging environments.
- Flip a fault's `live` flag after the containment contract passes.
- Run `python simulation/faults/inject.py <fault_name>` against the staging environment.
- Propose new faults to `simulation/faults/registry.py` (PR required, @platform-architect review).

**May not:**
- Touch any prod resource directly.
- Inject a fault that would make `tests/saboteur_containment_contract.py` go red.
- Declare `live=True` without a passing containment contract run on record.
- Operate outside a named drill window (ad-hoc fault injection outside a scheduled drill is not
  in scope).

---

## Verification

`python simulation/check_isolation.py` gives a quick health check of the simulation layer:
required docs exist, no runbooks reference prod, and the fault registry satisfies the isolation
invariants. This is CI-gated (`.github/workflows/ci.yml`).

`tests/saboteur_containment_contract.py` is the authoritative mechanical gate. The check_isolation
script is a supplementary summary, not a replacement.
