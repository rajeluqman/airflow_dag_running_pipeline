"""Trigger-only hub DAG for the Volve pipeline (Databricks + MLflow compute).

Operator + connection reference ONLY. The notebook/MLflow run body lives in the Volve repo's
own Databricks job, never here (see CLAUDE.md §1, cross_stack_contract.py).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connections.connection_ids import DATABRICKS_VOLVE  # noqa: E402

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

with DAG(
    dag_id="volve_trigger",
    description="Trigger-only hub DAG for the Volve pipeline (Databricks + MLflow).",
    schedule=None,  # TODO Fasa 2: set real cadence once the Databricks run is registered
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["control-plane", "volve", "trigger-only"],
) as dag:
    trigger_volve_databricks_run = DatabricksSubmitRunOperator(
        task_id="trigger_volve_databricks_run",
        databricks_conn_id=DATABRICKS_VOLVE,
        # TODO Fasa 2: replace with the real notebook_task/existing_cluster_id config once the
        # Volve + MLflow job is registered. Placeholder only — no real job config yet.
        json={"TODO_FASA_2": "real run config not yet registered"},
    )
