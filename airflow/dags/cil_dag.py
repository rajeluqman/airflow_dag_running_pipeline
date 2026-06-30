"""Trigger-only hub DAG for the CIL pipeline (DuckDB -> Snowflake).

Operator + connection reference ONLY. The CIL repo's own dbt/Snowflake logic stays in the CIL
repo (see CLAUDE.md §1, cross_stack_contract.py). This file does not run a query, transform, or
import any CIL business logic — it triggers CIL's own job from outside.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connections.connection_ids import SNOWFLAKE_CIL  # noqa: E402

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="cil_trigger",
    description="Trigger-only hub DAG for the CIL pipeline (DuckDB -> Snowflake).",
    schedule=None,  # TODO Fasa 2: set real cadence once CIL's own schedule is confirmed
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["control-plane", "cil", "trigger-only"],
) as dag:
    trigger_cil_pipeline = BashOperator(
        task_id="trigger_cil_pipeline",
        # TODO Fasa 2: replace with the real trigger mechanism (e.g. a Snowflake task call or
        # the CIL repo's own CI dispatch) once decided. conn_id is sourced from the
        # secrets-backend indirection (architecture/SECRETS_BACKEND.md), never hardcoded.
        bash_command=f"echo 'TODO Fasa 2: trigger CIL pipeline via conn_id={SNOWFLAKE_CIL}'",
    )
