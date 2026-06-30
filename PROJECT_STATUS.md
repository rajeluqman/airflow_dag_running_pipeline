# Project Status — Control-Plane Airflow Lab

---

## ▶ RESUME HERE (checkpoint — read this before reading source code)

**Date:** 2026-06-30  
**Branch:** `framework/fasa-1-scaffold` → **PR #1** open for Opus review  
**Fasa:** 1 scaffold complete — all gates green, PR #1 at github.com/rajeluqman/airflow_dag_running_pipeline/pull/1  

### What was just done

Fasa 1 scaffold built end-to-end on `framework/fasa-1-scaffold`. All 15 deliverables written,
all gates verified green. PR open to `main` for Opus design review.

### Immediate next task

**Fasa 2 — wire first real trigger: home-credit Glue job.**  
- Fill in `airflow/dags/home_credit_dag.py`: real `job_name` (from the home-credit repo's Glue
  job registration) and `aws_conn_id=GLUE_HOME_CREDIT` connected to a real staging AWS account.
- Set up `airflow/connections/.env` with `AIRFLOW_CONN_GLUE_HOME_CREDIT` pointing to staging.
- Run `home_credit_trigger` DAG and confirm the Glue job starts in staging.
- Verify `tests/cross_stack_contract.py` stays green after the real job name lands.

### Gate suite status (last verified: 2026-06-30)

| Gate | Status |
|------|--------|
| `tests/cross_stack_contract.py` | ✅ GREEN |
| `tests/saboteur_containment_contract.py` | ✅ GREEN |
| `tests/cost_guard.py` | ✅ GREEN |
| `tests/env_promotion_contract.py` | ✅ GREEN |
| `tests/doc_reference_contract.py` | ✅ GREEN |
| `python scripts/gen_repo_map.py --check` | ✅ GREEN |
| `python simulation/check_isolation.py` | ✅ GREEN |
| `ruff check .` | ✅ GREEN |
| `py_compile` (all .py files) | ✅ GREEN |

### What is NOT yet done (future Fasas)

- **Fasa 2:** Wire the 5 real trigger connections (starting with home-credit Glue).
- **Fasa 3:** Provision real cloud staging infra via Terraform (`infra/terraform/staging/`).
  Provision MWAA. Swap secrets backend to `SecretsManagerBackend`.
- **Fasa 4:** First live chaos drill — flip one fault's `live=True`, run @saboteur vs
  @sre-incident-commander, record MTTR in `simulation/MTTR_SCORECARD.md`.

---

## Fasa map

| Fasa | Scope | Status |
|------|-------|--------|
| 0 | Build authority: `architecture/control_plane_lab/00_MASTER_SPEC.md` + `01_OPUS_DECISIONS.md` | ✅ Done (Opus authored) |
| 1 | Scaffold: this file and all 15 deliverables | ✅ Done — PR open |
| 2 | First real triggers wired, connections live | ⏳ Next |
| 3 | Terraform staging infra + MWAA + SecretsManagerBackend | 🔒 After Fasa 2 |
| 4 | First live chaos drill (MTTR-scored, staging-only) | 🔒 After Fasa 3 |

---

## Fasa 1 deliverable checklist

1. ✅ `.gitignore` (committed to main)
2. ✅ `CLAUDE.md` (full operating environment, hook-backed)
3. ✅ `.claude/settings.json` + `.claude/hooks/governance_guard.py`
4. ✅ `.claude/agents/` (8 agent files)
5. ✅ `airflow/dags/` (5 trigger-stub DAGs)
6. ✅ `airflow/connections/connection_ids.py` + `.env.example`
7. ✅ `architecture/SECRETS_BACKEND.md`
8. ✅ `tests/cross_stack_contract.py`
9. ✅ `tests/saboteur_containment_contract.py`
10. ✅ `tests/cost_guard.py`
11. ✅ `tests/env_promotion_contract.py`
12. ✅ `tests/doc_reference_contract.py`
13. ✅ `simulation/faults/registry.py` + `inject.py` + `reset.py`
14. ✅ `simulation/ISOLATION_CONTRACT.md` + `check_isolation.py`
15. ✅ `simulation/MTTR_SCORECARD.md` + `simulation/runbooks/` (2 skeleton runbooks)
16. ✅ `architecture/CROSS_STACK_CONTRACT.md` + `REPO_REGISTRY.md`
17. ✅ `architecture/ADR/` (ADR-001 through ADR-010)
18. ✅ `scripts/gen_repo_map.py` + `architecture/REPO_MAP.md` (generated)
19. ✅ `scripts/sync_docs_to_confluence.py` + `confluence/00_START_HERE.md` + `01_ARCHITECTURE_DECISIONS.md`
20. ✅ `learning/CURRICULUM.md` + `LEARNING_LOG.md`
21. ✅ `observability/README.md` + `observability/alerts/slack_alert.py`
22. ✅ `.github/workflows/ci.yml`
23. ✅ `PROJECT_STATUS.md`, `COST_LOG.md`, `DECISION_LOG.md`, `INFRA_LIMITS_LOG.md`, `INTERVIEW_GUIDE.md`
