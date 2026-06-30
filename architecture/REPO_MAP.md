# REPO_MAP — generated navigation index

> **GENERATED — do not hand-edit.** `python scripts/gen_repo_map.py` rebuilds it from
> ground truth; CI runs `--check` and fails if this file is stale. Purpose is extracted
> from each file's own docstring / first heading / leading comment; *Uses* and *Used by*
> are parsed (`ast` for Python), never authored.
>
> **This is a pointer, not a cache.** It tells you which file to open — then READ THAT
> FILE FRESH before you edit or assert about it (ANTI-SHORTCUT PROTOCOL, CLAUDE.md §3). A
> pointer trusted without opening the file is just a bigger stale cache.
>
> Not mapped (by design): `.github/`, `.gitignore`, `.claude/settings.json`.

**67 files mapped.**

## Fasa-0 planning (build authority — Opus)

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `architecture/control_plane_lab/00_MASTER_SPEC.md` | Control-Plane Airflow Lab — MASTER SPEC (Fasa 0, Opus) | — | — |
| `architecture/control_plane_lab/01_OPUS_DECISIONS.md` | Opus Decisions — Control-Plane Airflow Lab (signed-off ruling) | — | — |
| `architecture/control_plane_lab/02_SONNET_BUILD_KICKOFF.md` | Sonnet Build Kickoff — Control-Plane Airflow Lab (Fasa 1) | — | — |
| `architecture/control_plane_lab/_source_to_port/doc_reference_contract.py` | Doc-reference contract — deterministic gate against documentation drift. | — | — |
| `architecture/control_plane_lab/_source_to_port/gen_repo_map.py` | Repo-map generator — the NAVIGATION half of the ANTI-SHORTCUT PROTOCOL (see CLAUDE.md). | — | — |
| `architecture/control_plane_lab/_source_to_port/sync_docs_to_confluence.py` | Publish the curated onboarding doc set to Confluence as living documentation. | — | — |

## Architecture Decision Records

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `architecture/ADR/ADR-001-trigger-only-dag-pattern.md` | ADR-001 — Trigger-only DAG pattern | — | — |
| `architecture/ADR/ADR-002-secrets-backend-abstraction.md` | ADR-002 — Secrets-backend abstraction (two-layer indirection) | — | — |
| `architecture/ADR/ADR-003-heterogeneous-stack-preservation.md` | ADR-003 — Preserve heterogeneous stacks; never homogenize | — | — |
| `architecture/ADR/ADR-004-saboteur-staging-containment.md` | ADR-004 — Saboteur staging-only containment (hard boundary) | — | — |
| `architecture/ADR/ADR-005-cost-circuit-breaker-auto-teardown.md` | ADR-005 — Cost circuit-breaker with mandatory auto-teardown | — | — |
| `architecture/ADR/ADR-006-env-promotion-gate.md` | ADR-006 — Env-promotion gate (staging drill green before prod) | — | — |
| `architecture/ADR/ADR-007-single-airflow-hub.md` | ADR-007 — Single Airflow hub for all 5 pipelines | — | — |
| `architecture/ADR/ADR-008-connection-id-indirection.md` | ADR-008 — Connection ID indirection via connection_ids.py | — | — |
| `architecture/ADR/ADR-009-conversational-language.md` | ADR-009 — Conversational language: English default, Manglish opt-in | — | — |
| `architecture/ADR/ADR-010-token-efficiency-session-discipline.md` | ADR-010 — Token-efficiency and session discipline | — | — |

## Architecture docs (record)

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `architecture/CROSS_STACK_CONTRACT.md` | Cross-Stack Contract — the trigger-only boundary | — | — |
| `architecture/REPO_REGISTRY.md` | Repo Registry — the 5 pipelines this control plane orchestrates | — | — |
| `architecture/SECRETS_BACKEND.md` | Secrets Backend — the codespace→MWAA one-config-swap path | — | — |

## Airflow DAGs (trigger-only)

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `airflow/dags/cil_dag.py` | Trigger-only hub DAG for the CIL pipeline (DuckDB -> Snowflake). | connection_ids.py | — |
| `airflow/dags/home_credit_dag.py` | Trigger-only hub DAG for the home-credit pipeline (AWS Glue / PySpark compute). | connection_ids.py | — |
| `airflow/dags/olist_dag.py` | Trigger-only hub DAG for the olist pipeline (Azure Databricks / ADLS compute). | connection_ids.py | — |
| `airflow/dags/paysim_dag.py` | Trigger-only hub DAG for the paysim pipeline (Databricks SQL / PySpark+Delta compute). | connection_ids.py | — |
| `airflow/dags/volve_dag.py` | Trigger-only hub DAG for the Volve pipeline (Databricks + MLflow compute). | connection_ids.py | — |

## Connections / secrets-backend indirection

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `airflow/connections/.env.example` | — | — | — |
| `airflow/connections/__init__.py` | (no module docstring) | — | — |
| `airflow/connections/connection_ids.py` | Single source of truth for this repo's Airflow connection IDs. | — | cil_dag.py, home_credit_dag.py, olist_dag.py, paysim_dag.py, volve_dag.py |

## Saboteur faults (staging-only)

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `simulation/faults/__init__.py` | (no module docstring) | — | — |
| `simulation/faults/inject.py` | Fault injection dispatcher — the @saboteur half of every fault in registry.py. | registry.py | — |
| `simulation/faults/registry.py` | Fault registry — the single source of truth saboteur_containment_contract.py and | — | check_isolation.py, cost_guard.py, inject.py, reset.py, saboteur_containment_contract.py |
| `simulation/faults/reset.py` | Fault reset dispatcher — the reversible half of every fault in registry.py. | registry.py | — |

## Incident runbooks

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `simulation/runbooks/databricks_cluster_kill_staging.md` | Runbook — databricks_cluster_kill_staging | — | — |
| `simulation/runbooks/glue_job_throttle_staging.md` | Runbook — glue_job_throttle_staging | — | — |

## Simulation / chaos-range docs

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `simulation/ISOLATION_CONTRACT.md` | Isolation Contract — Chaos-Range Containment Rules | — | — |
| `simulation/MTTR_SCORECARD.md` | MTTR Scorecard — Chaos-Range Drill History | — | — |

## Scripts

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `scripts/gen_repo_map.py` | Repo-map generator — the NAVIGATION half of the ANTI-SHORTCUT PROTOCOL (see CLAUDE.md §3). | — | — |
| `scripts/sync_docs_to_confluence.py` | Publish the curated onboarding doc set to Confluence as living documentation. | — | — |
| `simulation/__init__.py` | (no module docstring) | — | — |
| `simulation/check_isolation.py` | Simulation-layer isolation health check. | registry.py | — |

## Tests / contracts

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `tests/cost_guard.py` | Cost guard — the aggressive cost circuit-breaker (owner decision #5: "credits > convenience", | registry.py | — |
| `tests/cross_stack_contract.py` | Cross-stack contract — proves every DAG in this repo is trigger-only. | — | — |
| `tests/doc_reference_contract.py` | Doc-reference contract — deterministic gate against documentation drift. | — | — |
| `tests/env_promotion_contract.py` | Env-promotion contract — no direct prod edit; promotion requires staging-green + MTTR. | — | — |
| `tests/saboteur_containment_contract.py` | Saboteur-containment contract — the hard safety boundary of this repo. | registry.py | — |

## Governance hooks

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `.claude/hooks/governance_guard.py` | Governance guard — PreToolUse hook protecting the governed-file map (CLAUDE.md §8, | — | — |

## Cabinet agents

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `.claude/agents/cikgu.md` | name: cikgu | — | — |
| `.claude/agents/data-quality-steward.md` | name: data-quality-steward | — | — |
| `.claude/agents/finops-agent.md` | name: finops-agent | — | — |
| `.claude/agents/platform-architect.md` | name: platform-architect | — | — |
| `.claude/agents/platform-engineer.md` | name: platform-engineer | — | — |
| `.claude/agents/saboteur.md` | name: saboteur | — | — |
| `.claude/agents/scope-guardian.md` | name: scope-guardian | — | — |
| `.claude/agents/sre-incident-commander.md` | name: sre-incident-commander | — | — |

## Confluence sync + onboarding

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `confluence/00_START_HERE.md` | Start Here — Control-Plane Airflow Lab | — | — |
| `confluence/01_ARCHITECTURE_DECISIONS.md` | Architecture Decisions — Control-Plane Airflow Lab | — | — |

## Observability

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `observability/README.md` | Observability — Control-Plane Airflow Lab | — | — |
| `observability/alerts/slack_alert.py` | Slack alert stub for drill events and DAG failures. | — | — |

## Learning

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `learning/CURRICULUM.md` | Curriculum — Control-Plane Airflow Lab Teaching Path | — | — |
| `learning/LEARNING_LOG.md` | Learning Log — Control-Plane Airflow Lab | — | — |

## Top-level docs

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `CLAUDE.md` | CLAUDE.md — Operating Environment for airflow_dag_running_pipeline | — | — |
| `COST_LOG.md` | Cost Log — Control-Plane Airflow Lab | — | — |
| `DECISION_LOG.md` | Decision Log — Control-Plane Airflow Lab | — | — |
| `INFRA_LIMITS_LOG.md` | Infrastructure Limits Log — Control-Plane Airflow Lab | — | — |
| `INTERVIEW_GUIDE.md` | Interview Guide — Control-Plane Airflow Lab | — | — |
| `PROJECT_STATUS.md` | Project Status — Control-Plane Airflow Lab | — | — |
| `README.md` | airflow_dag_running_pipeline | — | — |

## Other

| File | Purpose | Uses | Used by |
|------|---------|------|---------|
| `ruff.toml` | — | — | — |
