#!/usr/bin/env python3
"""Cost guard — the aggressive cost circuit-breaker (owner decision #5: "credits > convenience",
architecture/control_plane_lab/01_OPUS_DECISIONS.md). Trial cloud credits are finite; a runaway
Databricks cluster or always-on Snowflake warehouse is an existential cost for this project.

Checks every fault declared in simulation/faults/registry.py (enumerated in full):
  1. auto_teardown must be a non-empty, specific statement of what gets torn down/suspended.
  2. budget_ceiling_usd must be a positive number — every drill needs a declared ceiling, not
     an open-ended "we'll watch it."

Stdlib only ($0, no deps). Exit 0 = every drill has teardown + ceiling. Exit 1 = a gap.

Run: python tests/cost_guard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _load_faults():
    from simulation.faults.registry import FAULTS  # local import: needs sys.path set above
    return FAULTS


def check() -> list[str]:
    errors: list[str] = []
    faults = _load_faults()

    if not faults:
        errors.append("simulation/faults/registry.py: FAULTS is empty — dead gate, nothing to check")
        return errors

    for fault in faults:
        if not fault.auto_teardown or not fault.auto_teardown.strip():
            errors.append(f"{fault.name}: auto_teardown is empty — every drill needs a declared teardown/suspend step")
        if not isinstance(fault.budget_ceiling_usd, (int, float)) or fault.budget_ceiling_usd <= 0:
            errors.append(f"{fault.name}: budget_ceiling_usd={fault.budget_ceiling_usd!r} — must be a positive number")

    return errors


def main(argv: list[str]) -> int:
    errors = check()
    if errors:
        print(f"COST GUARD: {len(errors)} violation(s)\n")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    faults = _load_faults()
    total_ceiling = sum(f.budget_ceiling_usd for f in faults)
    print(f"COST GUARD: OK — {len(faults)} fault(s) checked, all have auto-teardown + budget ceiling "
          f"(combined ceiling ${total_ceiling:.2f}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
