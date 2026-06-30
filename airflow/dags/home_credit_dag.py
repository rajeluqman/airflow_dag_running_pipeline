"""Trigger-only hub DAG for the home-credit pipeline (AWS Glue / PySpark compute).

Operator + connection reference ONLY. The PySpark transform body lives in the home-credit
repo's own Glue job script, never here (see CLAUDE.md §1, cross_stack_contract.py).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from connections.connection_ids import GLUE_HOME_CREDIT  # noqa: E402

from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

with DAG(
    dag_id="home_credit_trigger",
    description="Trigger-only hub DAG for the home-credit pipeline (AWS Glue).",
    schedule=None,  # TODO Fasa 2: set real cadence once the Glue job is registered
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["control-plane", "home-credit", "trigger-only"],
) as dag:
    trigger_home_credit_glue_job = GlueJobOperator(
        task_id="trigger_home_credit_glue_job",
        job_name="TODO_FASA_2_home_credit_glue_job",  # TODO Fasa 2: real Glue job name
        aws_conn_id=GLUE_HOME_CREDIT,
        region_name="us-east-1",  # TODO Fasa 2: confirm once AWS/Glue staging is provisioned
    )
