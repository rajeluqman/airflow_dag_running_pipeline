# ADR-002 — Secrets-backend abstraction (two-layer indirection)

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

DAGs need to reference external connections (Glue endpoint, Databricks workspace URL, Snowflake
account) without embedding credentials in code. The environment progresses from a Codespace-local
dev loop (Fasa 1–2) to a managed MWAA deployment (Fasa 3+). The indirection strategy must work
in both without any DAG-code change at promotion time.

## Decision

Two-layer indirection:

1. **Python layer (`airflow/connections/connection_ids.py`):** symbolic constants (`GLUE_HOME_CREDIT`,
   `DATABRICKS_OLIST`, etc.) are the only thing a DAG imports. No URL, no token, no account ID
   appears in DAG source.

2. **Backend layer (Airflow native secrets backend):** the mapping from symbolic connection ID to
   actual credentials is resolved by whichever backend is configured via
   `AIRFLOW__SECRETS__BACKEND`:
   - Codespace / local: `EnvironmentVariablesBackend` — credentials live in `.env` (gitignored)
     as `AIRFLOW_CONN_<ID>` env vars, documented in `airflow/connections/.env.example`.
   - MWAA (Fasa 3+): `SecretsManagerBackend` — credentials live in AWS Secrets Manager, never
     on disk.

Promotion from Codespace to MWAA is a single env-var swap in the MWAA environment config. Zero
DAG code changes required.

## Consequences

- **Positive:** No credentials ever appear in committed code; `.env` is gitignored and enforced
  by the CI committed-secret guard (`.github/workflows/ci.yml`).
- **Positive:** DAG files are identical between environments — the indirection is entirely at the
  infra/config layer.
- **Enforced:** `tests/cross_stack_contract.py` verifies that every DAG imports from
  `connections` (the indirection module), not hardcoded strings.
- **Trade-off:** Developers must set up the `.env` file locally using `.env.example` as the
  template before any DAG can connect to a real endpoint.

Full rationale: `architecture/SECRETS_BACKEND.md`.
