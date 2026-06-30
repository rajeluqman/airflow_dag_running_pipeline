"""Trigger-only hub DAG for the olist pipeline (Azure Databricks / ADLS compute).

Operator + connection reference ONLY. The ADLS/PySpark transform body lives in the olist
repo's own Databricks notebook/job, never here (see CLAUDE.md §1, cross_stack_contract.py).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connections.connection_ids import DATABRICKS_OLIST  # noqa: E402

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator

with DAG(
    dag_id="olist_trigger",
    description="Trigger-only hub DAG for the olist pipeline (Azure Databricks).",
    schedule=None,  # TODO Fasa 2: set real cadence once the Databricks job is registered
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["control-plane", "olist", "trigger-only"],
) as dag:
    trigger_olist_databricks_job = DatabricksRunNowOperator(
        task_id="trigger_olist_databricks_job",
        databricks_conn_id=DATABRICKS_OLIST,
        job_id=0,  # TODO Fasa 2: real Databricks job_id once the olist job is registered
    )
