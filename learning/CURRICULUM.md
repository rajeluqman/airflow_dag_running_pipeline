# Curriculum — Control-Plane Airflow Lab Teaching Path

> This is the teaching-lab half of this repo (see `confluence/00_START_HERE.md` §What this repo
> is). The curriculum follows the `@cikgu` teaching formula: **mental-model first → debug path →
> syntax last**. Each module builds on the previous; the chaos-range drills (Module 4) require
> Modules 1–3 as prerequisites.

---

## Module 1 — Control-Plane Mental Model

**Goal:** Understand what a trigger-only control plane is and why it exists.

1. Read `architecture/REPO_REGISTRY.md` — the 5 pipelines, their stacks, their operators.
2. Read `architecture/CROSS_STACK_CONTRACT.md` — the trigger-only boundary and why it's a
   load-bearing rule, not a style preference.
3. Read `architecture/SECRETS_BACKEND.md` — the two-layer secrets indirection.
4. Read `airflow/connections/connection_ids.py` and one DAG (`airflow/dags/home_credit_dag.py`).

**Check:** Can you explain, without reading the code, why the DAG imports a constant instead of a
string literal, and what happens to that constant when Airflow resolves the connection?

---

## Module 2 — Reading and Debugging DAGs

**Goal:** Be able to read an Airflow DAG, trace a failure, and identify the fix location.

1. Read all 5 DAGs in `airflow/dags/`. Note the operator type, task ID, and conn_id in each.
2. Run `python tests/cross_stack_contract.py` — observe what it checks and what "green" looks
   like.
3. **Drill (trigger-only boundary):** Add a `pandas` import to one DAG file. Run the contract.
   Observe the failure. Remove the import. Contract green again.
4. Understand the `sys.path.insert` trick in each DAG: why it's there, what it solves, and what
   would break if it were removed.

**Check:** Given a DAG failure like "connection not found: glue_home_credit", trace every layer
a developer must check: the operator call, the connection_ids.py constant, the `.env` file, and
the Airflow backend config.

---

## Module 3 — Governance, Gates, and the Anti-Shortcut Protocol

**Goal:** Understand the gate suite and why mechanical enforcement beats willpower.

1. Read `CLAUDE.md` §1–3 (STOP-GATE, anti-pattern table, ANTI-SHORTCUT PROTOCOL).
2. Read all 5 contracts in `tests/`. For each, articulate: what does it check? what does a red
   exit mean? what would you need to fix?
3. Run the full gate suite locally:
   ```
   python tests/cross_stack_contract.py
   python tests/saboteur_containment_contract.py
   python tests/cost_guard.py
   python tests/env_promotion_contract.py
   python tests/doc_reference_contract.py
   python scripts/gen_repo_map.py --check
   python simulation/check_isolation.py
   ```
4. Read `simulation/faults/registry.py`. Understand every field in the `Fault` dataclass.

**Check:** Why does `saboteur_containment_contract.py` check `prod_credential_refs == ()` rather
than just `environment == "staging"`? What attack path does the extra check close?

---

## Module 4 — Chaos-Range Drills (Fasa 4+)

**Goal:** Run a live drill, diagnose the injected fault, restore service, and record MTTR.

> **Prerequisites:** Modules 1–3 complete. At least one fault in `simulation/faults/registry.py`
> has `live=True` (Fasa 4+ only). Staging cloud environment provisioned (Fasa 3+).

1. Review `simulation/ISOLATION_CONTRACT.md` — understand the containment rules before any drill.
2. @saboteur flips one fault's `live` flag and runs `python simulation/faults/inject.py <name>`.
   `tests/saboteur_containment_contract.py` must stay green throughout.
3. @sre-incident-commander detects the fault via `observability/` signals, consults the relevant
   runbook under `simulation/runbooks/`, diagnoses, and restores via
   `python simulation/faults/reset.py <name>`.
4. Record MTTR in `simulation/MTTR_SCORECARD.md`. Review what went well and what was slow.
5. A staging drill MTTR is the prerequisite for any prod promotion (`tests/env_promotion_contract.py`).

**Check:** After the drill, can you explain why the fault was contained to staging, what the
auto-teardown would have done if MTTR had exceeded the budget ceiling, and what you'd fix in the
runbook for the next drill?

---

## Teaching formula (applies to every module)

- **Mental model before debug.** Understand the architecture before running a command.
- **Debug before syntax.** Know what failure mode you're chasing before reading error messages
  character by character.
- **Syntax last.** Look up the specific operator argument or config key only once you know exactly
  what you're configuring and why.

`@cikgu` is available for guided sessions through any of the above modules. Invoke in the
conversational interface; learning is recorded in `learning/LEARNING_LOG.md`.
