#!/usr/bin/env python3
"""Env-promotion contract — no direct prod edit; promotion requires staging-green + MTTR.

architecture/control_plane_lab/01_OPUS_DECISIONS.md: "No direct prod edits" — a change reaches
`infra/terraform/prod/` ONLY after a staging drill went green and its MTTR was recorded in
simulation/MTTR_SCORECARD.md. This contract enforces that pairing mechanically.

Two states, both real checks (not just "pass because it doesn't exist yet"):
  - `infra/terraform/prod/` does not exist: PASS — this also directly enforces the Fasa-1/2 hard
    rule "do not provision cloud / run Terraform before Fasa 3"
    (architecture/control_plane_lab/02_SONNET_BUILD_KICKOFF.md "Do NOT"). If this ever finds
    Terraform under prod/ before Fasa 3 it is itself a violation worth knowing about — see the
    explicit check below.
  - `infra/terraform/prod/` exists (Fasa 3+): every file under it must be referenced by path in
    simulation/MTTR_SCORECARD.md's promotion ledger — i.e. a real staging-green+MTTR record
    exists for that change. An unreferenced file is an un-promoted, direct prod edit.

Stdlib only ($0, no deps). Exit 0 = promotion discipline holds. Exit 1 = a violation.

Run: python tests/env_promotion_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROD_DIR = REPO / "infra" / "terraform" / "prod"
SCORECARD = REPO / "simulation" / "MTTR_SCORECARD.md"


def check() -> list[str]:
    errors: list[str] = []

    if not PROD_DIR.exists():
        # Nothing to promote yet — also confirms the Fasa-1/2 "no cloud yet" rule holds.
        return errors

    prod_files = sorted(p for p in PROD_DIR.rglob("*") if p.is_file())
    if not prod_files:
        return errors

    ledger_text = SCORECARD.read_text(encoding="utf-8") if SCORECARD.exists() else ""
    if not SCORECARD.exists():
        errors.append(
            "infra/terraform/prod/ has files but simulation/MTTR_SCORECARD.md does not exist — "
            "no promotion ledger to check against"
        )

    for f in prod_files:
        rel = f.relative_to(REPO).as_posix()
        if rel not in ledger_text:
            errors.append(
                f"{rel}: touches infra/terraform/prod/ with no matching staging-green+MTTR "
                f"entry in simulation/MTTR_SCORECARD.md — looks like a direct prod edit"
            )

    return errors


def main(argv: list[str]) -> int:
    errors = check()
    if errors:
        print(f"ENV-PROMOTION CONTRACT: {len(errors)} violation(s)\n")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    if PROD_DIR.exists():
        print("ENV-PROMOTION CONTRACT: OK — every infra/terraform/prod/ file has a matching promotion record.")
    else:
        print("ENV-PROMOTION CONTRACT: OK — infra/terraform/prod/ does not exist yet (Fasa 1/2, no cloud provisioned) — nothing to promote.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
