# ADR-005 — Cost circuit-breaker with mandatory auto-teardown

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

This repo's chaos drills run on real cloud accounts with real trial credits. A drill that spins up
a Glue job or Databricks cluster and never tears it down could exhaust the entire trial budget in
one session. The control needs to be structural, not procedural — relying on the operator to
remember to teardown is the gap that costs real money.

## Decision

Every fault definition in `simulation/faults/registry.py` must declare:

- `auto_teardown`: a non-empty string describing the automated teardown command/mechanism that
  runs if MTTR exceeds the budget ceiling.
- `budget_ceiling_usd`: a positive float. This is the maximum spend for one drill run. Once the
  ceiling is reached, the teardown fires automatically — the drill ends, win or lose.

`tests/cost_guard.py` enforces both fields before any drill starts. @finops-agent owns the
credit-watch role and is the escalation point for any drift from expected spend.

## Consequences

- **Positive:** No drill can run as an open-ended cloud expense. The worst-case cost of any single
  drill is known upfront and bounded.
- **Positive:** Auto-teardown removes the human memory dependency from cost safety — the gate
  fires even if the operator forgets.
- **Requires:** Every new fault added to the registry must specify a realistic teardown command
  before it can be declared live. A `TODO Fasa N` teardown string fails `cost_guard.py`.
- **Limitation (Fasa 1):** No faults are live yet; `cost_guard.py` passes trivially because all
  budget ceilings are declared on non-live faults. The real enforcement begins at Fasa 4 when
  the first fault goes live.

Full rationale: `architecture/control_plane_lab/01_OPUS_DECISIONS.md` §Cost guard.
