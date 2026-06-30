#!/usr/bin/env python3
"""Governance guard — PreToolUse hook protecting the governed-file map (CLAUDE.md §8,
architecture/control_plane_lab/01_OPUS_DECISIONS.md §Governed-file map).

This is NOT a substitute for the real gates (tests/*_contract.py). Those prove correctness
mechanically and are what CI actually fails on. This hook is the EDIT-TIME half: it fires before
a Write/Edit/MultiEdit lands, names which rule the target path is governed by and why, so the
rule is visible at the moment of the edit rather than only discovered later when a contract goes
red. Cheap awareness now beats an expensive red CI run later.

Enforcement level is deliberately split in two, not uniform "block everything governed":
  - HARD BLOCK (exit 2): only `infra/terraform/prod/*`. This is the one rule stated as
    absolute, with no legitimate exception path other than "go through env_promotion_contract.py
    / the IaC pipeline" — there is no such thing as a justified direct prod edit in this repo's
    model. Inert today (the path does not exist until Fasa 3) but armed and testable now.
  - ADVISORY (exit 0, stderr reminder): every other governed pattern. DAGs, faults, ADRs, and
    the contract scripts themselves are all under active, iterative, *expected* development
    during Fasa 1+ — hard-blocking them here would fight the normal build process the governed
    map is supposed to protect. Their real protection is the matching contract script
    (cross_stack_contract.py, saboteur_containment_contract.py, the ADR-as-historical-record
    convention, "don't weaken a gate" review discipline) — this hook just makes sure nobody
    edits them without being told, in the moment, which rule applies.

Hook contract (Claude Code PreToolUse): JSON on stdin shaped like
  {"tool_name": "Edit", "tool_input": {"file_path": "...", ...}, ...}
Exit 0 = allow (stderr may still carry an advisory shown to the user/agent).
Exit 2 = block; stderr is fed back as the reason.
Exit 0 with no matching pattern = silent allow (most edits touch nothing governed).

Also runnable standalone (no stdin hook payload) to print the governed-file map:
  python .claude/hooks/governance_guard.py --list
"""

from __future__ import annotations

import fnmatch
import json
import sys

# (glob pattern, rule, why, hard_block)
GOVERNED: list[tuple[str, str, str, bool]] = [
    (
        "airflow/dags/*.py",
        "DAGs must stay trigger-only",
        "paired with tests/cross_stack_contract.py — no SQL/PySpark transform body, "
        "no import of any pipeline repo's business logic. Operator + connection ref ONLY.",
        False,
    ),
    (
        "simulation/faults/*",
        "saboteur blast-radius — containment-critical",
        "every fault must be staging-only, declare a blast radius, and have a reversible "
        "reset. tests/saboteur_containment_contract.py is the real gate; this is the reminder.",
        False,
    ),
    (
        "infra/terraform/prod/*",
        "prod env — no edit without the env-promotion gate",
        "promotion to prod happens ONLY via tests/env_promotion_contract.py "
        "(staging-green + MTTR recorded). There is no direct-edit exception.",
        True,
    ),
    (
        "architecture/ADR/*",
        "orchestration doctrine — historical record",
        "ADRs are amended via a dated addendum section, not a silent rewrite of the "
        "original decision (see adr-addendum-parity in project memory).",
        False,
    ),
    (
        "architecture/CROSS_STACK_CONTRACT.md",
        "orchestration doctrine",
        "this doc is the human-readable counterpart to tests/cross_stack_contract.py — "
        "keep them in sync if you change one.",
        False,
    ),
    (
        "tests/*_contract.py",
        "the gates themselves",
        "don't weaken a gate to make it pass — if a check is wrong, fix it with the same "
        "rigor you'd want applied to the thing it's checking, and say so in the commit message.",
        False,
    ),
    (
        "tests/cost_guard.py",
        "the gates themselves",
        "don't weaken a gate to make it pass — cost_guard.py is what stands between this "
        "repo and a runaway cloud bill.",
        False,
    ),
]

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def _match(file_path: str) -> tuple[str, str, str, bool] | None:
    for pattern, rule, why, hard in GOVERNED:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path, "*/" + pattern):
            return pattern, rule, why, hard
    return None


def _print_map() -> int:
    print("Governed-file map (CLAUDE.md §8):\n")
    for pattern, rule, why, hard in GOVERNED:
        level = "HARD BLOCK" if hard else "advisory"
        print(f"  [{level}] {pattern}\n      rule: {rule}\n      why:  {why}\n")
    return 0


def main(argv: list[str]) -> int:
    if "--list" in argv[1:]:
        return _print_map()

    raw = sys.stdin.read()
    if not raw.strip():
        return 0  # no hook payload, no path to check — nothing to do

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0  # not a hook invocation we understand — fail open, never block on noise

    if payload.get("tool_name") not in EDIT_TOOLS:
        return 0

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    hit = _match(file_path)
    if hit is None:
        return 0

    pattern, rule, why, hard = hit
    if hard:
        print(
            f"governance_guard: BLOCKED — {file_path} matches governed pattern '{pattern}'\n"
            f"  rule: {rule}\n  why:  {why}",
            file=sys.stderr,
        )
        return 2

    print(
        f"governance_guard: advisory — {file_path} matches governed pattern '{pattern}'\n"
        f"  rule: {rule}\n  why:  {why}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
