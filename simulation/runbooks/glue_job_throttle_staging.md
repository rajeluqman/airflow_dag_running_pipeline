# Runbook — glue_job_throttle_staging

> **Fault:** `glue_job_throttle_staging` (see `simulation/faults/registry.py`)  
> **Blast radius:** staging AWS Glue — throttles the home-credit staging Glue job to simulate
> AWS Glue concurrent-run limits being hit.  
> **Reversible:** Yes — `simulation/faults/reset.py glue_job_throttle_staging` removes the
> throttle policy.  
> **Budget ceiling:** $5.00 USD (auto-teardown fires if MTTR exceeds ceiling)

---

## What this fault simulates

AWS Glue enforces concurrent-run limits per account. When a large batch of home-credit jobs
lands simultaneously, subsequent runs are throttled with `ConcurrentRunsExceededException`.
The Airflow DAG task (`home_credit_dag.py → trigger_home_credit_pipeline`) will show a
failed state. This drill tests whether @sre-incident-commander can distinguish a throttle
(transient, retry-able) from a job logic failure (requires a code fix in the home-credit repo).

---

## Detection

1. Open the Airflow UI (staging) or check DAG run logs.
2. The `trigger_home_credit_pipeline` task is in FAILED state.
3. Log contains: `ConcurrentRunsExceededException` or `ThrottlingException`.
4. Cross-check: is the home-credit Glue job still in a RUNNING state from a prior trigger?

**Observability signals:** `observability/README.md` §Glue metrics — look for
`ConcurrentRunsExceeded` count metric in CloudWatch (staging namespace only).

---

## Diagnosis

- Is this a genuine throttle (prior job still running) or a different Glue error?
- Check AWS Glue staging console: how many concurrent runs are active?
- Is the `aws_conn_id=GLUE_HOME_CREDIT` connection resolving correctly (backend issue vs Glue issue)?

---

## Restore procedure

1. Wait for the running Glue job to complete (if it's a genuine concurrent-limit hit, resolution
   is automatic once the prior run finishes).
2. If the prior run is stuck: manually stop it via AWS Glue staging console.
3. Re-trigger the DAG in Airflow UI (staging) or via `airflow dags trigger home_credit_trigger`.
4. Confirm the new run reaches RUNNING → SUCCEEDED state.
5. Run `python simulation/faults/reset.py glue_job_throttle_staging` to remove the injected
   throttle policy.

---

## Post-drill

Record MTTR in `simulation/MTTR_SCORECARD.md`. Note: was the throttle vs. logic failure
distinction clear from the logs alone, or did you need to check the Glue console?

---

## Status (Fasa 1)

This runbook is a **skeleton** — the fault is declared `live=False` in the registry. The restore
procedure above is written for when the fault goes live at Fasa 4. Steps marked with AWS console
access require the staging AWS connection to be configured (`airflow/connections/.env`).
