# MTTR Scorecard — Chaos-Range Drill History

> Every live drill run by @saboteur + @sre-incident-commander is recorded here. This file is
> required by `tests/env_promotion_contract.py` for any prod promotion — a staging drill MTTR
> on record is the gate for every prod resource provisioned in `infra/terraform/prod/`.
>
> Entries are never deleted or sanitized. A drill that went badly is more valuable to keep than
> a perfect drill — that's the teaching value.

---

## Scorecard

| # | Date | Fault | MTTR (min) | Budget used (USD) | Outcome | Notes |
|---|------|-------|-----------|-------------------|---------|-------|
| — | — | — | — | — | — | No drills yet — Fasa 4 is the first live drill. |

---

## Entry format (for future drills)

```
| N | YYYY-MM-DD | <fault_name from registry.py> | <minutes from inject to restore> | $<amount> | GREEN / RED / PARTIAL | <what went well / what was slow / runbook gap identified> |
```

**Outcome key:**
- **GREEN:** Service restored within budget ceiling; runbook followed; MTTR recorded.
- **RED:** Budget ceiling hit before restore; auto-teardown fired; post-mortem required.
- **PARTIAL:** Fault contained but restore was manual / out-of-runbook; runbook needs update.
