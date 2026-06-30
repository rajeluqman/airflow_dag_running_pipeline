# Runbook — databricks_cluster_kill_staging

> **Fault:** `databricks_cluster_kill_staging` (see `simulation/faults/registry.py`)  
> **Blast radius:** staging Databricks — terminates the cluster running the olist or paysim
> staging job mid-run.  
> **Reversible:** Yes — `simulation/faults/reset.py databricks_cluster_kill_staging` restarts
> the target cluster.  
> **Budget ceiling:** $10.00 USD (auto-teardown fires if MTTR exceeds ceiling)

---

## What this fault simulates

A Databricks cluster hosting a long-running olist (ADLS) or paysim (Delta/SQL) job is killed
mid-run — simulating spot-instance preemption or an accidental cluster termination. The Airflow
DAG tasks (`olist_dag.py` or `paysim_dag.py`) will show a FAILED state. This drill tests
whether @sre-incident-commander can distinguish a cluster kill (infra-level, restart the cluster
and re-trigger) from a job logic failure (requires a fix in the olist/paysim repo).

---

## Detection

1. The `trigger_olist_pipeline` or `trigger_paysim_pipeline` Airflow task is in FAILED state.
2. Task log contains: `ClusterError`, `CLUSTER_TERMINATED`, or `Run state: TERMINATED`.
3. Databricks Jobs UI (staging workspace): the run shows `CLUSTER_ERROR` as the failure reason.

**Observability signals:** `observability/README.md` §Databricks metrics — look for
cluster-state events in the Databricks staging workspace event log.

---

## Diagnosis

- Is this a cluster kill (infra) or a job exception (logic)?
- Databricks Jobs UI → Run details → Failure reason: `CLUSTER_ERROR` = infra; `USER_CODE_ERROR` = logic.
- Was the cluster running on spot instances? Spot preemption is recoverable by restarting on
  on-demand or a new spot allocation.

---

## Restore procedure

1. In Databricks staging workspace: navigate to Compute → find the terminated cluster.
2. Restart the cluster (or create a new one if it was an ephemeral job cluster).
3. In Airflow: clear the failed task and re-trigger (or re-run from the failed task).
4. Confirm the Databricks job reaches SUCCEEDED state.
5. Run `python simulation/faults/reset.py databricks_cluster_kill_staging` to confirm the reset
   is recorded.

---

## Post-drill

Record MTTR in `simulation/MTTR_SCORECARD.md`. Note: how long did it take to distinguish infra
failure from logic failure? Was the Databricks event log readable from the Airflow task log, or
did you need to go to the Databricks UI directly?

---

## Status (Fasa 1)

This runbook is a **skeleton** — the fault is declared `live=False` in the registry. Steps
requiring Databricks staging access need `AIRFLOW_CONN_DATABRICKS_OLIST` or
`AIRFLOW_CONN_DATABRICKS_PAYSIM` configured in `airflow/connections/.env`.
