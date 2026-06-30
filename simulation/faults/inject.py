#!/usr/bin/env python3
"""Fault injection dispatcher — the `@saboteur` half of every fault in registry.py.

Fasa 1 = skeleton: every fault is `live=False`. Calling inject() before Fasa 4's first real
drill is a deliberate, loud NotImplementedError — never a silent no-op — so a premature call
fails obviously instead of pretending to have done something on staging.
"""

from __future__ import annotations

import sys

from registry import FAULTS


def inject(fault_name: str) -> None:
    matches = [f for f in FAULTS if f.name == fault_name]
    if not matches:
        raise ValueError(f"unknown fault: {fault_name!r} — see simulation/faults/registry.py")
    fault = matches[0]
    if fault.environment != "staging":
        raise RuntimeError(f"fault {fault_name!r} is not declared staging-only — refusing to inject")
    if not fault.live:
        raise NotImplementedError(
            f"fault {fault_name!r} is planned but not live yet (Fasa 1 skeleton) — "
            "see simulation/faults/registry.py"
        )
    raise NotImplementedError("Fasa 4: wire the real injection mechanism here")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python inject.py <fault_name>")
    inject(sys.argv[1])
