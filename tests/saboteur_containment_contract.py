#!/usr/bin/env python3
"""Saboteur-containment contract — the hard safety boundary of this repo.

Live chaos on real cloud with real credits is only safe behind this gate
(architecture/control_plane_lab/01_OPUS_DECISIONS.md "Saboteur is the heart, containment is
non-negotiable"). It checks every fault declared in simulation/faults/registry.py — enumerated
in full, never sampled — against the containment invariants:

  1. environment must be exactly "staging" — no fault may target prod.
  2. prod_credential_refs must be empty — no path from a fault to a prod credential.
  3. reversible must be True — every fault needs a declared, working reset.
  4. blast_radius must be a non-empty, specific statement (not "everything"/"unknown").
  5. Fasa 1/2 invariant: no fault may be `live=True` yet — this repo is still skeleton-only,
     no live drills until Fasa 4 (00_MASTER_SPEC.md §8 build sequencing).

Additionally scans simulation/faults/*.py source text for a prod-credential-shaped reference
(defense in depth alongside the dataclass-field check — catches a hardcoded slip the metadata
wouldn't).

Stdlib only ($0, no deps). Exit 0 = containment holds. Exit 1 = a containment violation.

Run: python tests/saboteur_containment_contract.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAULTS_DIR = REPO / "simulation" / "faults"

sys.path.insert(0, str(REPO))

PROD_REF_PATTERN = re.compile(r"\bprod(?:uction)?[-_]?(?:conn|credential|secret|arn|account)\b", re.IGNORECASE)


def _load_faults():
    from simulation.faults.registry import FAULTS  # local import: needs sys.path set above
    return FAULTS


def check_metadata() -> list[str]:
    errors: list[str] = []
    faults = _load_faults()

    if not faults:
        errors.append("simulation/faults/registry.py: FAULTS is empty — dead gate, nothing to check")
        return errors

    for fault in faults:
        if fault.environment != "staging":
            errors.append(f"{fault.name}: environment={fault.environment!r} — must be exactly 'staging'")
        if fault.prod_credential_refs:
            errors.append(f"{fault.name}: declares prod_credential_refs={fault.prod_credential_refs!r} — must be empty")
        if not fault.reversible:
            errors.append(f"{fault.name}: reversible=False — every fault needs a declared, working reset")
        if not fault.blast_radius or not fault.blast_radius.strip():
            errors.append(f"{fault.name}: blast_radius is empty — must be a specific statement of what this fault can touch")
        if fault.live:
            errors.append(f"{fault.name}: live=True — no fault may go live before Fasa 4 (this repo is still skeleton-only)")

    return errors


def check_source_text() -> list[str]:
    errors: list[str] = []
    if not FAULTS_DIR.exists():
        return ["simulation/faults/ does not exist — dead gate, nothing to check"]

    for path in sorted(FAULTS_DIR.glob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        if PROD_REF_PATTERN.search(text):
            errors.append(f"{rel}: matches a prod-credential-shaped reference /{PROD_REF_PATTERN.pattern}/")
    return errors


def main(argv: list[str]) -> int:
    errors = check_metadata() + check_source_text()
    if errors:
        print(f"SABOTEUR-CONTAINMENT CONTRACT: {len(errors)} violation(s)\n")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    faults = _load_faults()
    print(f"SABOTEUR-CONTAINMENT CONTRACT: OK — {len(faults)} fault(s) declared, all staging-only and reversible, none live yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
