# ADR-001 — Trigger-only DAG pattern

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

This repo orchestrates 5 existing pipeline repos (CIL, home-credit, olist, paysim, Volve) across
4 cloud stacks. Each pipeline repo owns its own business logic, tested and versioned
independently. The question is where DAG code lives and what it is allowed to contain.

## Decision

DAG files under `airflow/dags/` are **trigger-only**: they contain an Airflow DAG definition, one
or more operator instantiations that *start* a job already defined in the pipeline's own repo,
and a reference to a connection ID sourced from `airflow/connections/connection_ids.py`. Nothing
else.

A DAG file may NEVER contain: a SQL statement, a PySpark/Pandas transform call, an import of any
pipeline repo's own packages, or a hardcoded credential.

## Consequences

- **Positive:** Each pipeline's own CI/tests remain the authoritative coverage for its logic. This
  repo's blast radius is limited to scheduling and triggering — it does not need credentials
  covering the data itself, only the job-start API.
- **Positive:** The 4-stack heterogeneity is preserved naturally — this repo never needs to
  understand what Glue vs Databricks vs Snowflake do internally.
- **Enforced mechanically:** `tests/cross_stack_contract.py` runs on every CI pass and denies
  business-logic-shaped imports, SQL/PySpark patterns, and missing connection-ID indirection.
  `.claude/hooks/governance_guard.py` surfaces the rule at edit-time.
- **Trade-off:** Any fix to business logic must go to the pipeline's own repo, never here. This
  is the intended constraint, not a limitation to work around.

Full rationale: `architecture/control_plane_lab/01_OPUS_DECISIONS.md` §DAGs are trigger-only.
