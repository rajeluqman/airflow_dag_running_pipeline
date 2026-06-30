# Cross-Stack Contract — the trigger-only boundary

> Human-readable counterpart to `tests/cross_stack_contract.py`. Keep them in sync — if this doc
> changes, check whether the script's checks still match it, and vice versa
> (`.claude/hooks/governance_guard.py` reminds on edit; nothing enforces sync automatically yet).

## The boundary

This repo orchestrates 5 pipeline repos across 4 real cloud stacks. The single most important
rule, stated in `architecture/control_plane_lab/00_MASTER_SPEC.md` §1 and
`architecture/control_plane_lab/01_OPUS_DECISIONS.md`: **DAGs are trigger-only.**

A DAG file under `airflow/dags/` may contain:
- An Airflow `DAG` definition (schedule, default args, tags).
- One or more operator instantiations — the operator that *starts* a job already defined and
  running in the pipeline's own repo (`GlueJobOperator`, `DatabricksRunNowOperator`,
  `DatabricksSubmitRunOperator`, `BashOperator` for a CIL-side trigger call).
- A reference to a connection ID sourced from `airflow/connections/connection_ids.py` (the
  secrets-backend indirection, see `architecture/SECRETS_BACKEND.md`).

A DAG file under `airflow/dags/` may NEVER contain:
- A SQL statement (any `SELECT`/`INSERT`/`UPDATE`/`DELETE`/`CREATE TABLE`/`MERGE` text).
- A PySpark/Pandas transform call (`spark.sql(`, `.withColumn(`, `.toDF(`, a pandas import).
- An `import` of any of the 5 pipeline repos' own packages.
- A hardcoded credential, connection string, or secret literal.

## Why this is the boundary, not a style preference

Each pipeline repo (CIL, home-credit, olist, paysim, Volve) owns its own transform logic, tested
and versioned independently of this repo. If transform logic crept into this repo's DAGs:
- The pipeline repo's own tests/CI would no longer cover the logic that actually runs.
- This repo would need credentials/compute access to every pipeline's data, multiplying its
  blast radius for no benefit — the whole point of *triggering* is that the trigger doesn't need
  to know how the job works, only that it should start.
- The 4-stack heterogeneity (`architecture/REPO_REGISTRY.md`) would erode toward whatever this
  repo's authors found easiest to write inline, defeating the "preserve each stack, never
  homogenize" rule.

## How it's enforced

- **Mechanically, every run:** `tests/cross_stack_contract.py` — parses every DAG file with
  `ast`, denies business-logic-shaped imports, regex-scans for SQL/PySpark patterns, and
  confirms the connection-ID indirection is used. CI-gated (`.github/workflows/ci.yml`).
- **At edit-time:** `.claude/hooks/governance_guard.py` prints the rule when
  `airflow/dags/*.py` is touched, so it's visible before the edit lands, not just after CI runs.
- **By design, not just by gate:** `@platform-engineer` (the agent that builds DAGs) has this
  boundary written into its own role definition (`.claude/agents/platform-engineer.md`), and
  `@scope-guardian` has a hard veto if business logic is proposed to move into this repo.
