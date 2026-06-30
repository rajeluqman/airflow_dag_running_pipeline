"""Trigger-only hub DAG for the paysim pipeline (Databricks SQL / PySpark+Delta compute).

Operator + connection reference ONLY. The PySpark+Delta transform body lives in the paysim
repo's own Databricks job, never here (see CLAUDE.md §1, cross_stack_contract.py).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connections.connection_ids import DATABRICKS_PAYSIM  # noqa: E402

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator

with DAG(
    dag_id="paysim_trigger",
    description="Trigger-only hub DAG for the paysim pipeline (Databricks SQL / PySpark+Delta).",
    schedule=None,  # TODO Fasa 2: set real cadence once the Databricks job is registered
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["control-plane", "paysim", "trigger-only"],
) as dag:
    trigger_paysim_databricks_job = DatabricksRunNowOperator(
        task_id="trigger_paysim_databricks_job",
        databricks_conn_id=DATABRICKS_PAYSIM,
        job_id=0,  # TODO Fasa 2: real Databricks job_id once the paysim job is registered
    )
