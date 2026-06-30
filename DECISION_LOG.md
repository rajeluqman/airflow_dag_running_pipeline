# Decision Log — Control-Plane Airflow Lab

> Running log of implementation decisions made during the build that are too specific for an ADR
> but worth recording so a future session knows why something looks the way it does.
> ADR-worthy decisions get their own file in `architecture/ADR/`; this log captures the others.

---

## Fasa 1 scaffold decisions (2026-06-30)

### D-001 — governance_guard.py uses ADVISORY for most patterns, hard-block only for prod

**Decision:** `.claude/hooks/governance_guard.py` exits 0 (advisory, with stderr warning) for
all governed patterns except `infra/terraform/prod/*` (exit 2, hard block).

**Why:** The hard block pattern doesn't exist yet in Fasa 1 (no `infra/terraform/prod/`
directory), so wiring the hook at all required the advisory-only path to be safe for the build
session itself. Hard blocking `airflow/dags/*.py` edits during the session that builds those
files would be self-defeating.

**Trade-off accepted:** Advisory means a human (or assistant) can override with intent. The
contract scripts (`tests/cross_stack_contract.py`) are the authoritative enforcement — the hook
is an edit-time reminder, not the final word.

---

### D-002 — sys.path trick in DAG files avoids airflow.connections collision

**Decision:** Each DAG file uses `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`
to add `airflow/` to the Python path, then imports `from connections.connection_ids import X`
(not `from airflow.connections.connection_ids import X`).

**Why:** The `airflow` package namespace is owned by Apache Airflow itself. Importing as
`airflow.connections` would collide with Airflow's own `airflow.connections` module. The
`sys.path` trick makes the import resolve as `connections.connection_ids` (a local module under
`airflow/`), avoiding the namespace collision while keeping the file layout intuitive.

---

### D-003 — doc_reference_contract ALLOW entry for airflow/connections/.env

**Decision:** Added `"airflow/connections/.env": "gitignored by design ..."` to the ALLOW dict
in `tests/doc_reference_contract.py`.

**Why:** The `.env.example` file references `airflow/connections/.env` by name (documenting the
runtime file that a developer must create locally). The contract scanned for this path and found
it absent from the repo — correctly, because it's gitignored. The ALLOW entry records the
deliberate absence rather than treating it as a drift violation.

---

### D-004 — infra/terraform/ NOT created in Fasa 1 (scope guardian veto)

**Decision:** `infra/terraform/staging/` and `infra/terraform/prod/` directories were considered
and explicitly rejected for Fasa 1.

**Why:** Fasa 1 is scaffold + Codespace-local only. Terraform is Fasa 3. Creating the directories
early would (a) mislead anyone reading the repo about the current provisioning state, (b) risk
triggering env_promotion_contract.py's prod-gate logic prematurely, and (c) violate the
STOP-GATE in `CLAUDE.md` §1 which explicitly forbids provisioning real cloud before Fasa 3.

---

### D-005 — REPO_MAP.md excluded from doc_reference_contract scan scope

**Decision:** `architecture/REPO_MAP.md` is in `scripts/gen_repo_map.py`'s EXCLUDE set and is
not in the doc_reference_contract's default scan paths.

**Why:** REPO_MAP.md is generated content. Its backtick path references are file stems and role
labels extracted from actual files — they're pointers, not doc references in the sense the
contract checks. Including it in the scan would produce false positives from auto-generated
table cells that happen to look like path patterns.
