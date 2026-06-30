# Observability — Control-Plane Airflow Lab

> **Fasa 1 state:** No live Airflow process and no real cloud jobs yet. This directory is a
> skeleton that documents *where* observability signals will come from and *what* @sre-incident-
> commander should look at during a drill. Signal collection and alerting are wired at Fasa 3+.

---

## Signal sources by stack

| Stack | Signal source | What to watch | Drill relevance |
|---|---|---|---|
| Airflow (control plane) | Airflow task logs, DAG run state | Task FAILED/UP_FOR_RETRY, SLA miss | First place to look for any pipeline failure |
| AWS Glue (home-credit) | CloudWatch Logs (`/aws-glue/jobs/`), Glue job metrics | `ConcurrentRunsExceeded`, job FAILED, DPU cost | Throttle vs logic failure distinction |
| Azure Databricks (olist) | Databricks Jobs UI, cluster event log | `CLUSTER_ERROR` vs `USER_CODE_ERROR`, run state | Cluster kill vs code failure distinction |
| Databricks SQL/Delta (paysim) | Databricks Jobs UI, Delta transaction log | Job run state, Delta write failures | Schema drift, transaction conflict |
| Databricks+MLflow (Volve) | MLflow experiment UI, Databricks run log | Training run status, artifact registration | Model training failure vs artifact issue |
| Snowflake (CIL) | Snowflake Query History, ACCOUNT_USAGE views | Failed queries, warehouse credit burn | Connection failure vs query failure |

---

## During a drill: @sre-incident-commander checklist

1. **Start in Airflow.** Which DAG, which task, what state? Task log: what's the last line?
2. **Read the error class.** Is it a connection error (backend config issue), an infra error
   (cluster kill, throttle), or a logic error (code in the pipeline repo)?
3. **Cross-check the stack.** Go to the relevant signal source (table above) to confirm the
   failure reason.
4. **Consult the runbook.** `simulation/runbooks/<fault_name>.md` has the diagnosis and restore
   procedure for each declared fault.
5. **Restore and verify.** Follow the runbook's restore procedure. Confirm the Airflow task
   reaches SUCCESS state.
6. **Record MTTR.** Time from fault injection to confirmed restore → `simulation/MTTR_SCORECARD.md`.

---

## Slack alerts (Fasa 3+)

`observability/alerts/slack_alert.py` — stub for sending Slack notifications when a DAG task
fails or an MTTR threshold is exceeded. Wired up at Fasa 3 alongside the MWAA deployment.
Requires `SLACK_WEBHOOK_URL` in the environment (gitignored, like all credentials).
