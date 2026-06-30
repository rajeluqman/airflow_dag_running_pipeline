# ADR-007 — Single Airflow hub for all 5 pipelines

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

Each of the 5 pipeline repos is independently scheduled today. When cross-pipeline dependencies
exist (e.g., CIL downstream of paysim's feature table), coordinating them requires a shared
orchestration layer. The options are: (a) one Airflow hub for all 5, (b) one Airflow per
pipeline, or (c) each pipeline handles its own scheduling with no shared layer.

## Decision

ONE Airflow hub (this repo) orchestrates all 5 pipelines. Each pipeline gets exactly one trigger
DAG here. There is no plan for per-pipeline Airflow instances managed by this repo — that would
multiply infrastructure cost and split scheduling visibility.

`@platform-architect` owns the orchestration topology: how triggers compose, how staging/prod
promotion works across all 5. Routine DAG edits go to `@platform-engineer`, never bypassing the
cross-stack design constraint.

## Consequences

- **Positive:** All cross-pipeline scheduling is visible in one Airflow UI. Debugging a
  cross-pipeline dependency failure starts here, then drills into the relevant pipeline repo.
- **Positive:** One set of connection secrets to manage (one backend config swap at MWAA
  promotion time) rather than 5 parallel Airflow setups.
- **Requires:** Every pipeline trigger DAG must be kept current with that pipeline's operator API.
  If home-credit changes its Glue job name, `airflow/dags/home_credit_dag.py` must be updated.
- **Limitation (Fasa 1):** The hub runs locally in Codespace with no live Airflow process — DAGs
  are syntax-checked and contract-gated but not actually scheduled. MWAA provisioning is Fasa 3.
