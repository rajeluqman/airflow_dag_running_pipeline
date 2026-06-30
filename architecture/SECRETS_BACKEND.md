# Secrets Backend — the codespace→MWAA one-config-swap path

## What problem this solves

DAGs must never hardcode a credential, host, or secret (CLAUDE.md §7 "What NOT to commit").
But DAGs DO need to reference *which* connection to trigger through. The split that makes both
true at once: DAGs reference a **symbolic conn_id string** (`airflow/connections/connection_ids.py`)
and nothing else — resolution of that conn_id to a real secret happens entirely in Airflow's own
**secrets backend** configuration, which lives outside any DAG file.

This is the "baked-in day one" portability promise: moving this control plane from a codespace
to MWAA changes ONE config value. No DAG is touched, no connection ID is renamed.

## The two layers

1. **Python-level indirection (this repo, today):** `airflow/connections/connection_ids.py` is
   the single source of truth for every conn_id string used across the 5 trigger DAGs. A DAG
   imports a constant (e.g. `GLUE_HOME_CREDIT = "glue_home_credit"`) instead of typing
   `"glue_home_credit"` ad hoc — a rename is a one-file diff, not a five-file hunt.
2. **Backend-level indirection (Airflow's own mechanism):** Airflow resolves `conn_id` →
   credential via whichever secrets backend is configured for the environment. The conn_id
   string a DAG passes to an operator (`aws_conn_id=`, `databricks_conn_id=`) never changes —
   only the backend that answers "what does `glue_home_credit` actually resolve to" changes.

## The swap, concretely

| Environment | Backend | Config |
|---|---|---|
| Codespace (Fasa 1–2) | `airflow.secrets.environment_variables.EnvironmentVariablesBackend` | env vars shaped `AIRFLOW_CONN_<CONN_ID_UPPER>` — see `airflow/connections/.env.example` |
| MWAA (Fasa 3+ showcase runs) | `airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend` | a single `AIRFLOW__SECRETS__BACKEND` + `AIRFLOW__SECRETS__BACKEND_KWARGS` env var on the MWAA environment, pointing at AWS Secrets Manager entries named to match the same conn_id strings |

Both rows resolve the exact same conn_id strings from `connection_ids.py`. The swap is a
deployment-config change (one env var on the Airflow environment), never a code change.

## Local development today (Fasa 1)

No real Airflow process runs yet in Fasa 1 (that's Fasa 2's docker-compose deliverable) — the
DAG files are syntax-valid and statically checked (`tests/cross_stack_contract.py`,
`py_compile`) but not executed. `airflow/connections/.env.example` documents the env var shape
the `EnvironmentVariablesBackend` will expect once Fasa 2 stands up the local hub; copy it to
`airflow/connections/.env` (gitignored — never commit real values) when that lands.

## Why not a custom secrets module instead

A hand-rolled `get_secret(name)` helper was considered and rejected: Airflow already ships this
exact indirection as a first-class, pluggable subsystem (`[secrets] backend` /
`AIRFLOW__SECRETS__BACKEND`). Reimplementing it would duplicate functionality Airflow already
provides, add a second place for the same bug class to hide, and lose the actual MWAA
compatibility this design needs (MWAA expects the native backend interface, not a custom one).
