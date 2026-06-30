# Interview Guide — Control-Plane Airflow Lab

> Practical question set for assessing understanding of this repo's architecture, governance, and
> chaos-range design. Organized by depth tier: Tier 1 (reading comprehension), Tier 2 (debug
> path), Tier 3 (design judgment). Use in conjunction with `learning/CURRICULUM.md` — each
> tier maps to the curriculum modules.

---

## Tier 1 — Reading comprehension (Module 1)

These questions can be answered by reading the repo docs without running anything.

1. What are the three roles this repo plays simultaneously? Where does each role live in the
   directory structure?

2. Why do all 5 DAGs use different operators? What determines which operator a DAG uses?

3. Explain the two layers of the secrets-backend indirection. What is `connection_ids.py` for,
   and what does the Airflow secrets backend do with it?

4. Why is DAG-level business logic (SQL, PySpark) explicitly banned here when those tools are
   exactly what the pipeline repos use? What would break if a DAG imported pandas?

5. What is the difference between `tests/saboteur_containment_contract.py` and
   `simulation/check_isolation.py`? Which one is authoritative?

---

## Tier 2 — Debug path (Module 2–3)

These require understanding how failures propagate across the control plane.

6. A `home_credit_trigger` DAG task fails with "connection not found: glue_home_credit". Walk
   through every layer a developer must check, from the Airflow UI to the resolved credential.

7. `tests/cross_stack_contract.py` exits 1 with "DENY_IMPORT: pyspark found". What does that
   mean? What file needs to change, and why is pyspark banned if the pipeline repo uses it?

8. You add a new fault to `simulation/faults/registry.py` with `environment="production"`.
   Which contract catches it? What is the exact failure message you'd expect?

9. `python scripts/gen_repo_map.py --check` exits 1 with "REPO-MAP: STALE". What caused it?
   What is the single command to fix it? Why does CI run `--check` instead of regenerating?

10. You clone this repo on a new machine and run `python airflow/dags/home_credit_dag.py`. It
    imports successfully but would fail at runtime. Why? What file do you need to create first?

---

## Tier 3 — Design judgment (Module 1–4, cross-cutting)

These require understanding the *why* behind the architecture choices.

11. Why does this repo use ONE Airflow hub for all 5 pipelines rather than one Airflow per
    pipeline? What would you lose by splitting it?

12. The env-promotion contract passes trivially in Fasa 1–2 because `infra/terraform/prod/`
    doesn't exist. Is this a gap in the gate? How does the overall system still prevent an
    accidental prod edit in Fasa 1–2?

13. A team proposes adding a dbt transformation directly to a DAG file because "it's just one
    SQL query and it's faster than going back to the CIL repo". Which agents have a veto, which
    contract would catch it, and what's the actual argument against doing this?

14. The `cost_guard.py` enforces `budget_ceiling_usd > 0` and `auto_teardown`. Why isn't it
    enough to just tell the person running the drill to teardown manually when they're done?

15. You need to add a 6th pipeline (a new Kafka consumer) to the control plane. Walk through
    every file you'd need to touch, every gate that would run, and which agent needs to approve
    the cross-stack design before the PR merges.

---

## Scoring guide

- **Tier 1 (1–5):** Full marks = can read and explain the architecture without running code.
  Partial marks = can find the relevant files but can't explain the rationale.
  
- **Tier 2 (6–10):** Full marks = correctly traces the failure path to the root cause layer.
  Partial marks = identifies the right file but misses a layer in the chain.

- **Tier 3 (11–15):** Full marks = gives the design rationale, not just the mechanical answer.
  Partial marks = recites the rule without explaining why the rule exists.

A candidate who aces Tier 1–2 and engages thoughtfully with Tier 3 is ready to contribute to
Fasa 2 work. A candidate who can design a new Tier 3 question has internalized the architecture.
