# Start Here — Control-Plane Airflow Lab

## What this repo is

`airflow_dag_running_pipeline` is a 3-in-1:

1. **Control-plane.** ONE Airflow hub orchestrating 5 existing pipeline repos — CIL, home-credit,
   olist, paysim, Volve — across 4 real cloud stacks (AWS Glue, Azure Databricks, Databricks
   SQL/Delta, Snowflake). Every DAG here is **trigger-only**: it starts a job that already lives
   in its own pipeline repo. No business logic, no SQL, no PySpark transform body ever lives in
   this repo — see `architecture/CROSS_STACK_CONTRACT.md`.
2. **Teaching lab.** A curriculum (`learning/CURRICULUM.md`) built around the
   debug → troubleshoot → optimize → incident path across 4 heterogeneous stacks, taught
   mental-model-first, syntax-last.
3. **Live-chaos range.** `@saboteur` injects faults into a real **staging** cloud environment;
   `@sre-incident-commander` detects, diagnoses, and restores; the time-to-recover is scored in
   `simulation/MTTR_SCORECARD.md`. A fix only reaches **prod** after a staging drill goes green
   (`tests/env_promotion_contract.py`) — there is no direct prod edit.

## What it orchestrates

| Pipeline | Compute target | Trigger operator |
|---|---|---|
| home-credit | AWS Glue (PySpark) | `GlueJobOperator` |
| olist | Azure Databricks (ADLS) | `DatabricksRunNowOperator` |
| paysim | Databricks SQL / PySpark+Delta | `DatabricksRunNowOperator` |
| Volve | Databricks + MLflow | `DatabricksSubmitRunOperator` |
| CIL | DuckDB → Snowflake | bash/python trigger |

Full registry, including each pipeline's own repo and why its stack was kept heterogeneous
rather than homogenized: `architecture/REPO_REGISTRY.md`.

## How this repo is governed

- `CLAUDE.md` — the full operating environment: stop-gate, anti-shortcut protocol, token
  discipline, language convention, what-not-to-commit. Hook-backed by
  `.claude/hooks/governance_guard.py`.
- `.claude/agents/` — the cabinet: `@platform-architect` (ultimate veto on cross-stack design),
  `@scope-guardian` (hard veto on creep), `@platform-engineer`, `@sre-incident-commander`,
  `@saboteur`, `@finops-agent`, `@cikgu`.
- `tests/*_contract.py` + `tests/cost_guard.py` — the mechanical gates: trigger-only boundary,
  saboteur containment, cost ceilings, env-promotion discipline, doc-reference drift.

## How to run a drill (today vs. later)

**Today (Fasa 1 — this build):** there is no live Airflow process and no live fault yet. Every
fault in `simulation/faults/registry.py` is declared `live=False` — `simulation/faults/inject.py`
refuses to act on any of them. The skeleton (`simulation/ISOLATION_CONTRACT.md`,
`simulation/check_isolation.py`, `simulation/runbooks/`, `simulation/MTTR_SCORECARD.md`) exists
so the real drill loop has somewhere to record itself once it's live.

**Fasa 4 (the first real drill):** `@saboteur` will flip one fault's `live` flag, run
`simulation/faults/inject.py <fault_name>` against the **staging** environment only
(`tests/saboteur_containment_contract.py` must stay green throughout), and
`@sre-incident-commander` will detect, diagnose via `observability/`, and restore via
`simulation/faults/reset.py`, logging the result to `simulation/MTTR_SCORECARD.md`.

## Build status

See `PROJECT_STATUS.md`'s "▶ RESUME HERE" block for exactly where this repo's build currently
stands, and `architecture/control_plane_lab/` for the Fasa-0 build-authority docs this whole repo
was built from.
