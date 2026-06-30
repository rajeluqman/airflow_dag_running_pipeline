# CLAUDE.md — Operating Environment for `airflow_dag_running_pipeline`

> This file is hook-backed: `.claude/hooks/governance_guard.py` enforces the governed-file map
> below mechanically. Read this before touching any governed path. Build authority for the
> whole repo lives in `architecture/control_plane_lab/00_MASTER_SPEC.md` +
> `01_OPUS_DECISIONS.md` — this file operationalizes those rulings turn-by-turn.

## What this repo is

A control-plane (ONE Airflow hub orchestrating 5 pipeline repos — CIL, home-credit, olist,
paysim, Volve — across 4 real cloud stacks), a teaching lab (debug/troubleshoot/optimize/
incident path), and a live-chaos range (`@saboteur` vs `@sre-incident-commander`, MTTR-scored,
staging→prod promotion). DAGs in this repo are **trigger-only** — business logic never lives
here, it stays in each pipeline's own repo. Full identity: `architecture/control_plane_lab/00_MASTER_SPEC.md §1`.

---

## 1. STOP-GATE (ops version)

This repo's stop-gate is NOT about data lineage (this repo models no data — that gate belongs
to CIL and is deliberately dropped here, see §2). It is about three things that can do real,
hard-to-reverse damage on real cloud accounts with real credits:

**STOP and get explicit confirmation before:**
- Touching anything under `simulation/faults/` in a way that could reach a non-staging target —
  saboteur containment is the hard safety boundary of this whole repo (`01_OPUS_DECISIONS.md
  §Opus rulings`). If `saboteur_containment_contract.py` would go red, do not proceed; fix the
  fault definition first.
- Any direct edit under `infra/terraform/prod/` (once it exists, Fasa 3+) or any other prod
  resource. Promotion to prod happens ONLY through the env-promotion gate
  (`tests/env_promotion_contract.py`): staging-drill-green + MTTR recorded. There is no
  "just this once" direct prod edit.
- Anything that would put business logic, SQL, or a PySpark/Databricks transform body inside
  `airflow/dags/*.py`. That breaks the single most important boundary in this repo
  (`cross_stack_contract.py`) — DAGs are operator + connection-ref ONLY.
- Provisioning real cloud (Terraform apply, a real Glue/Databricks job, standing up MWAA) before
  Fasa 3. Fasa 1–2 are scaffold + codespace-local only.

If a gate (`tests/*_contract.py`, `tests/cost_guard.py`) would go red as a result of an action,
treat that as the stop signal — fix the underlying issue, never bypass the gate.

---

## 2. The anti-pattern this repo deliberately does NOT copy

CIL is a DATA repo (lineage/identity/Clean-ERD doctrine). This is an OPS repo. Do not port CIL's
data-content gates here — there is no data model in this repo to protect.

| CIL gate | This repo |
|---|---|
| lineage_contract / identity | ❌ dropped — repo models no data |
| Clean-ERD doctrine + data-architect | ❌ dropped — no new data models built here |
| boundary (reject Spark/Databricks) | ✅ ported but INVERTED — Glue/Databricks are REQUIRED here |
| anti-shortcut protocol | ✅ ported (§3 below) |
| repo-map navigation gate | ✅ ported (`scripts/gen_repo_map.py`) |
| doc-reference contract | ✅ ported (`tests/doc_reference_contract.py`) |

---

## 3. ANTI-SHORTCUT PROTOCOL (verbatim discipline — applies to every session)

This is the "no missing gap" engine. It is not advice — treat each rule as load-bearing.

1. **Read-before-touch.** Never edit, assert about, or make a decision based on a file you
   haven't opened fresh in the current turn. A pointer (REPO_MAP.md, a prior summary, your own
   memory of an earlier read) tells you WHICH file to open — it is never a substitute for
   opening it. A pointer trusted without opening the file is just a bigger stale cache.
2. **Enumerate, don't sample.** When scoping a check across a set (files, contracts, ADRs,
   connections), list the full set explicitly. State what you excluded and why — on the record,
   not silently dropped. (See `scripts/gen_repo_map.py`'s `EXCLUDE` set for the canonical
   pattern: the exclusion is a named decision, not an absence.)
3. **Reconcile-before-done.** Before declaring any task complete, restate the original scope as
   a numbered checklist and attach `file:line` or command-output evidence per item. No evidence
   = say "unverified", not "done". Verify gates by *running* them — never by trusting your own
   build report.
4. **Tag assumptions `(unverified)`.** Anything inferred rather than confirmed against a primary
   source (the spec docs, a command's actual output, a file you actually opened) gets tagged
   inline so a reader can separate fact from inference at a glance. ADRs reconstructed from
   spec rationale rather than real deliberation are tagged `(reconstructed — owner confirm)`.

**Why this matters here specifically:** this repo runs live chaos drills on real cloud accounts
with finite trial credits. A "missing gap" in a data repo is a wrong number in a dashboard; a
missing gap in this repo's saboteur-containment or cost-guard logic is a real, hard-to-reverse
cost or a fault that escapes staging. The protocol is the substitute for vigilance — gates not
willpower, code tak penat ("code doesn't get tired").

---

## 4. Token Discipline (mechanical, every turn)

- **Checkpoint-first.** Read `PROJECT_STATUS.md`'s "▶ RESUME HERE" block before reading source
  code at the start of a session. Resume from the checkpoint; don't cold-re-derive state that's
  already on record.
- **Max ~3 files per turn.** If a task needs more than ~3 files read to scope correctly, that's
  a signal to delegate the search (next bullet), not to read all of them inline.
- **Use the `Explore` subagent for "where is X."** Broad searches ("which DAG references this
  connection ID", "where is the budget ceiling enforced") go to a search subagent so the answer
  comes back as a pointer, not a context-window's worth of grep output.
- **Update the checkpoint before ending a turn.** `PROJECT_STATUS.md` should always reflect
  where the next session resumes from — that's the whole point of having it.

---

## 5. Token-efficiency & session discipline (ADR-010)

Full ruling: `architecture/ADR/ADR-010-token-efficiency-session-discipline.md`.

- **Model routing.** Heavy cross-stack orchestration design calls route to
  `@platform-architect` (Opus, ultimate veto). Minor rulings route to `@scope-guardian` or a
  Sonnet agent — or better, to a deterministic gate/contract script instead of spending a model
  call at all.
- **Gate-over-reread.** If a question can be answered by running a contract/gate script (exit
  code + message), run the gate. Don't re-read source files to manually re-derive an answer a
  script already gives deterministically.
- **Context-bar checkpointing.** When context usage crosses ~75% (red zone): stop, write the
  checkpoint to `PROJECT_STATUS.md`, and continue in a fresh session via the RESUME-HERE block
  rather than pushing further into a degraded-context turn.

---

## 6. Conversational language (ADR-009)

Full ruling: `architecture/ADR/ADR-009-conversational-language.md`.

English is the default for all conversation and every committed doc (ADRs, runbooks, this file,
`PROJECT_STATUS.md`). Manglish is opt-in per session — only switch into it if the user explicitly
uses it first in that session; never assume it from a prior session or from the owner's locale.
Committed documentation stays in English regardless of the conversational register used in chat.

---

## 7. What NOT to commit

- `.env`, `.env.*` (except `.env.example`) — connection secrets, API tokens.
- `**/connections/*.env`, `**/connections/*.secret` — resolved connection credentials.
- `*.tfstate*`, `.terraform/` — Terraform state holds resolved secrets/outputs in plaintext
  (becomes live once Fasa 3 stands up `infra/terraform/`).
- `__pycache__/`, `*.log`, any local credential file — see `.gitignore` for the full, enforced
  list. The CI committed-secret guard (`.github/workflows/ci.yml`) double-checks this on every
  push — a `.gitignore` entry is a courtesy to the local dev loop, not the actual backstop.
- The `GH_AIRFLOW` PAT itself — lives ONLY in the Codespace secret, never in a file, commit, or
  memory record. Use per-command: `GH_TOKEN=$GH_AIRFLOW gh ...` and
  `git push https://rajeluqman:${GH_AIRFLOW}@github.com/...`. NEVER `gh auth login --with-token`
  (persists globally), NEVER `git push -u` with the token embedded in the URL (writes it into
  `.git/config` on disk). Both slips happened before in `pipeline_retrofit` — see that repo's
  PROJECT_STATUS for the incident record.

## Intentionally committed

This repo is self-contained by design — a newcomer (or Opus, reviewing a Fasa PR) should be able
to understand the whole operating model from what's in the repo, without external context:
- `CLAUDE.md` (this file), `PROJECT_STATUS.md`, `DECISION_LOG.md`, `COST_LOG.md`,
  `INFRA_LIMITS_LOG.md`, `INTERVIEW_GUIDE.md` — the operating record.
- `learning/LEARNING_LOG.md` — the teaching-lab record (deliberately a log, not scrubbed).
- `architecture/ADR/*.md` — every architecture decision, including reconstructed ones (tagged).
- `simulation/MTTR_SCORECARD.md` and `simulation/runbooks/*.md` — drill history, kept even when
  a drill went badly; that's the teaching value.

---

## 8. Governed-file map (enforced by `.claude/hooks/governance_guard.py`)

| Protects | Why |
|---|---|
| `airflow/dags/*.py` | DAGs must stay trigger-only (paired with `cross_stack_contract.py`) |
| `simulation/faults/*` | saboteur blast-radius — containment-critical |
| `infra/terraform/prod/*` | prod env — no edit without the env-promotion gate (Fasa 3+) |
| `architecture/ADR/`, `architecture/CROSS_STACK_CONTRACT.md` | orchestration doctrine |
| `tests/*_contract.py`, `tests/cost_guard.py` | the gates themselves — don't weaken a gate to make it pass |

Full rationale: `architecture/control_plane_lab/01_OPUS_DECISIONS.md §Governed-file map`.
