# Infrastructure Limits Log — Control-Plane Airflow Lab

> Documents the cloud trial credit limits and any infrastructure quota constraints discovered
> during the build. This log prevents surprises: knowing the ceiling before a drill is the cost
> discipline (`architecture/ADR/ADR-005-cost-circuit-breaker-auto-teardown.md`).
>
> **Fasa 1 state:** No real cloud resources provisioned. Limits below are documented for
> planning purposes; exact values (unverified) should be confirmed by the repo owner when
> setting up cloud credentials for Fasa 3.

---

## Cloud trial limits (unverified — owner to confirm)

| Cloud | Trial type | Credit ceiling | Key limits | Expires |
|-------|-----------|---------------|-----------|---------|
| AWS | Free tier / trial | ~$300 USD (unverified) | Glue DPUs, Lambda invocations | (unverified) |
| Azure | Trial | ~$200 USD (unverified) | Databricks DBUs, ADLS storage | (unverified) |
| Databricks | Community/trial | (unverified) | DBUs per cluster, runtime hours | (unverified) |
| Snowflake | Trial | ~$400 credits (unverified) | Compute credits, storage GB | (unverified) |

**(unverified)** = not confirmed against actual account — verify before Fasa 3.

---

## Drill budget ceilings (from fault registry)

| Fault | Budget ceiling | Auto-teardown |
|-------|---------------|---------------|
| glue_job_throttle_staging | $5.00 USD | Documented in `simulation/runbooks/glue_job_throttle_staging.md` |
| databricks_cluster_kill_staging | $10.00 USD | Documented in `simulation/runbooks/databricks_cluster_kill_staging.md` |

---

## Quota incidents

*(None yet — first drill is Fasa 4.)*

---

## Entry format for future incidents

```
### YYYY-MM-DD — <cloud> quota incident

**Limit hit:** <what was exhausted>
**Impact:** <what failed / was blocked>
**Resolution:** <how it was resolved>
**Prevention:** <what to change in fault registry or drill playbook>
```
