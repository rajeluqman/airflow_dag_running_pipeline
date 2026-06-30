# Cost Log — Control-Plane Airflow Lab

> Running record of actual cloud spend incurred during drills and infrastructure provisioning.
> Costs are recorded by drill (linked to `simulation/MTTR_SCORECARD.md`) and by Fasa.
> Fasa 3+ adds Terraform-provisioned resources; Fasa 4+ adds drill costs.

---

## Summary

| Fasa | Cloud | Resources | Cost to date |
|------|-------|-----------|-------------|
| 1 | None | Codespace only (no real cloud) | $0.00 |
| 2 | TBD | First real trigger wired (home-credit Glue) | — |
| 3 | TBD | Terraform-provisioned staging infra | — |
| 4+ | TBD | Live drills | — |

**Total cloud spend to date: $0.00** (Fasa 1 — no real cloud resources provisioned)

---

## Per-drill cost entries (Fasa 4+)

*(No drills yet — see `simulation/MTTR_SCORECARD.md` for when the first drill runs.)*

---

## Entry format

```
### YYYY-MM-DD — Drill: <fault_name>

**Stack:** <AWS Glue / Azure Databricks / etc.>  
**Duration:** <time from inject to teardown>  
**Resources used:** <what ran: job, cluster, etc.>  
**Estimated cost:** $X.XX USD  
**Budget ceiling:** $Y.YY USD  
**Auto-teardown fired:** Yes / No  
**Notes:** <anything unusual about the spend>
```
