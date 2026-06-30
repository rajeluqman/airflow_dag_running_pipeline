"""Single source of truth for this repo's Airflow connection IDs.

Every constant here is a SYMBOLIC conn_id string only — never a credential, host, or secret.
DAGs under airflow/dags/ import these instead of typing connection-id strings ad hoc, so a
rename is a one-file diff instead of a five-file hunt.

Resolving a conn_id to a real credential happens entirely OUTSIDE this module, via Airflow's
own secrets-backend configuration (env-var backend in codespace today, swappable to AWS Secrets
Manager for MWAA later with zero change to this file or to any DAG). See
architecture/SECRETS_BACKEND.md for the full design and the one-config-swap path.
"""

from __future__ import annotations

# AWS Glue (home-credit)
GLUE_HOME_CREDIT = "glue_home_credit"

# Azure Databricks / ADLS (olist)
DATABRICKS_OLIST = "databricks_olist"

# Databricks SQL / PySpark+Delta (paysim)
DATABRICKS_PAYSIM = "databricks_paysim"

# Databricks + MLflow (Volve)
DATABRICKS_VOLVE = "databricks_volve"

# DuckDB -> Snowflake (CIL) — the trigger reaches CIL's own repo/job, never a literal warehouse
# session here (this repo stays trigger-only, see CLAUDE.md §1 STOP-GATE).
SNOWFLAKE_CIL = "snowflake_cil"
