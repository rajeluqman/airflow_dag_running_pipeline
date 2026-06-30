"""Simulation-layer isolation health check.

Companion to tests/saboteur_containment_contract.py (the authoritative mechanical gate) and
simulation/ISOLATION_CONTRACT.md (human-readable rules). This script gives a quick health
summary of the simulation skeleton itself — does the required scaffolding exist, and does the
fault registry hold its isolation invariants?

This is a SUMMARY script, not a replacement for saboteur_containment_contract.py. Run both.

Exit 0 = all checks pass. Exit 1 = one or more failures.

Run: python simulation/check_isolation.py
CI:  python simulation/check_isolation.py  (wired in .github/workflows/ci.yml)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SIM_DIR = REPO / "simulation"

# These files are the required simulation skeleton — check they exist
REQUIRED_DOCS = [
    SIM_DIR / "ISOLATION_CONTRACT.md",
    SIM_DIR / "MTTR_SCORECARD.md",
]

# Narrow prod-credential patterns that should NEVER appear in a runbook file.
# These are specific enough that a legitimate "staging vs prod" discussion won't match them.
PROD_CRED_PATTERNS = [
    re.compile(r"arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:"),  # real AWS ARN (has 12-digit account)
    re.compile(r"PROD_AWS_ACCESS|PROD_DATABRICKS_TOKEN|PROD_SNOWFLAKE_"),
    re.compile(r"-----BEGIN (RSA )?PRIVATE KEY"),
]

failures: list[str] = []


def check_required_docs() -> None:
    for doc in REQUIRED_DOCS:
        rel = doc.relative_to(REPO)
        if not doc.exists():
            failures.append(f"C1 MISSING required simulation doc: {rel}")
        else:
            print(f"  C1 OK: {rel}")


def check_runbook_isolation() -> None:
    runbooks_dir = SIM_DIR / "runbooks"
    if not runbooks_dir.exists():
        print("  C2 SKIP: simulation/runbooks/ not found")
        return
    runbooks = sorted(runbooks_dir.glob("*.md"))
    if not runbooks:
        print("  C2 OK: simulation/runbooks/ exists (no runbook files yet)")
        return
    for rb in runbooks:
        text = rb.read_text(encoding="utf-8")
        hit = False
        for pat in PROD_CRED_PATTERNS:
            if pat.search(text):
                failures.append(f"C2 PROD-CREDENTIAL pattern '{pat.pattern}' in runbook: {rb.name}")
                hit = True
                break
        if not hit:
            print(f"  C2 OK: {rb.name} — no prod-credential patterns found")


def check_fault_registry() -> None:
    sys.path.insert(0, str(REPO))
    try:
        from simulation.faults.registry import FAULTS
    except ImportError as exc:
        failures.append(f"C3 IMPORT ERROR — cannot load fault registry: {exc}")
        return
    for fault in FAULTS:
        name = fault.name
        if fault.environment != "staging":
            failures.append(f"C3 FAULT '{name}': environment={fault.environment!r} — must be 'staging'")
        elif fault.prod_credential_refs:
            failures.append(f"C3 FAULT '{name}': prod_credential_refs={fault.prod_credential_refs!r} — must be empty")
        else:
            print(f"  C3 OK: fault '{name}' — staging-only, no prod refs")


def main() -> int:
    print("SIMULATION ISOLATION CHECK")
    print("  C1: Required simulation docs")
    check_required_docs()
    print("  C2: Runbook prod-credential scan")
    check_runbook_isolation()
    print("  C3: Fault registry isolation invariants")
    check_fault_registry()

    if failures:
        print(f"\nSIMULATION ISOLATION: {len(failures)} failure(s):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nSIMULATION ISOLATION: OK — all checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
