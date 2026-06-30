# ADR-003 — Preserve heterogeneous stacks; never homogenize

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

The 5 pipelines use 4 different compute stacks: AWS Glue (home-credit PySpark batch), Azure
Databricks (olist ADLS workload), Databricks SQL/Delta (paysim streaming-shaped), and
Databricks+MLflow (Volve model training), with DuckDB/Snowflake for CIL's warehouse-style marts.
Each choice was made by that pipeline's own repo for workload-specific reasons. A natural reflex
when building a control plane is to standardize all 5 onto one stack.

## Decision

This repo NEVER homogenizes the 5 pipeline stacks. Each pipeline keeps its own compute target;
this repo only triggers it. The 4-stack heterogeneity is a deliberate feature of the teaching lab
— debugging a Glue throttle failure looks different from debugging a Databricks cluster kill, and
both are in-scope drills.

The 5 pipelines listed in `architecture/REPO_REGISTRY.md` are the permanent universe. No 6th
pipeline is added to this repo; no existing pipeline is re-platformed here.

## Consequences

- **Positive:** Each pipeline's compute team retains sovereignty over their stack choice. This
  repo has no standing to re-decide compute choices it did not originally make.
- **Positive:** The teaching lab covers 4 distinct failure modes across 4 stacks — more
  educational than a homogenized single-stack range.
- **Requires:** 4–5 different Airflow operator types (`GlueJobOperator`, `DatabricksRunNowOperator`,
  `DatabricksSubmitRunOperator`, `BashOperator`). Each must be imported correctly in its DAG.
- **Enforced by:** `@scope-guardian` has a hard veto on any change that would re-implement a
  pipeline's compute logic here or add a 6th pipeline.

Full rationale: `architecture/REPO_REGISTRY.md` §Why heterogeneous, not homogenized.
