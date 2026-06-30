# Architecture Decisions — Control-Plane Airflow Lab

> Consolidated hub for Confluence. Individual ADR files live under `architecture/ADR/` (not
> published to Confluence individually — this page is the onboarding-friendly summary). For
> full rationale on any decision, follow the ADR link.

---

## The 10 decisions that shape this repo

### ADR-001 — Trigger-only DAG pattern

Every DAG in `airflow/dags/` contains only an Airflow DAG definition, operator instantiation(s)
that *start* a job already defined in a pipeline repo, and a connection-ID constant. No SQL, no
PySpark, no business logic ever lives here. Enforced mechanically by `tests/cross_stack_contract.py`.

**Why it matters:** Keeps this repo's blast radius at scheduling/triggering. Each pipeline's own
CI stays authoritative for its logic.

---

### ADR-002 — Secrets-backend abstraction (two-layer indirection)

DAGs import symbolic constants from `airflow/connections/connection_ids.py`. Credentials are
resolved by Airflow's native secrets backend — `EnvironmentVariablesBackend` locally,
`SecretsManagerBackend` on MWAA. One env-var swap promotes between environments; zero DAG code
changes required.

**Why it matters:** No credential ever appears in committed code. Backend promotion is
infrastructure-only.

---

### ADR-003 — Preserve heterogeneous stacks; never homogenize

The 5 pipelines use 4 different compute stacks (Glue, Databricks, Databricks SQL/Delta,
Snowflake). This repo never re-decides those choices — it only triggers each stack's own job.
The 4-stack heterogeneity is the teaching lab's feature, not a problem to fix.

**Why it matters:** Compute sovereignty stays with each pipeline team. Debugging drills cover
4 distinct failure modes.

---

### ADR-004 — Saboteur staging-only containment (hard boundary)

Every fault in `simulation/faults/registry.py` must target staging only, hold no prod credential
refs, and be reversible. `tests/saboteur_containment_contract.py` enforces this. A fault that
would make the contract red does not land.

**Why it matters:** A fault that escapes staging on a trial cloud account is a hard-to-reverse
real cost or data incident.

---

### ADR-005 — Cost circuit-breaker with mandatory auto-teardown

Every fault must declare `budget_ceiling_usd > 0` and `auto_teardown` (non-empty). The teardown
fires automatically if MTTR exceeds the ceiling. `tests/cost_guard.py` enforces before any drill.
@finops-agent owns the credit-watch role.

**Why it matters:** No drill runs as an open-ended cloud expense. Worst-case cost is always known
upfront.

---

### ADR-006 — Env-promotion gate (staging drill green before prod)

Production changes require a staging drill green + MTTR recorded in `simulation/MTTR_SCORECARD.md`.
`tests/env_promotion_contract.py` enforces: if `infra/terraform/prod/` exists, every file there
must appear in the scorecard. No direct prod edit ever.

**Why it matters:** MTTR is a prerequisite for prod access. The chaos range earns the right to
prod by proving it can respond to staging failures.

---

### ADR-007 — Single Airflow hub for all 5 pipelines

ONE Airflow hub (this repo) orchestrates all 5 pipelines. Per-pipeline Airflow instances are
explicitly not in scope. All cross-pipeline scheduling is visible in one place. @platform-architect
owns the orchestration topology.

**Why it matters:** Single scheduling visibility point; one backend to configure; one source of
truth for cross-pipeline dependencies.

---

### ADR-008 — Connection ID indirection via `connection_ids.py`

`airflow/connections/connection_ids.py` is the only file that contains connection ID string
literals. Every DAG imports the constant. Renaming a connection is a one-file change. The
cross-stack contract verifies the import is used.

**Why it matters:** Eliminates the mismatch class of runtime connection errors and the maintenance
cost of grepping DAG files for string literals.

---

### ADR-009 — Conversational language: English default, Manglish opt-in

All committed documentation (ADRs, runbooks, CLAUDE.md, PROJECT_STATUS.md) is English. Manglish
is opt-in per session — only if the owner uses it first in that session. Prior sessions and locale
are not signals.

**Why it matters:** Committed docs stay readable by all collaborators and reviewers, regardless of
the language used in chat.

---

### ADR-010 — Token-efficiency and session discipline

Checkpoint-first (read PROJECT_STATUS.md RESUME-HERE before source), gate-over-reread (run a
contract script rather than re-reading source to answer a question), context-bar checkpointing at
75%, and model routing (@platform-architect/Opus for cross-stack design, Sonnet for routine
tasks).

**Why it matters:** Keeps sessions coherent and cost-efficient across the long Fasa build arc.

---

## Where to find individual ADRs

All 10 live in `architecture/ADR/` in the repo, numbered ADR-001 through ADR-010. They are the
primary record; this page is the onboarding summary.
