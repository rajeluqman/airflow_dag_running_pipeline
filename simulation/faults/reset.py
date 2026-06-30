#!/usr/bin/env python3
"""Fault reset dispatcher — the reversible half of every fault in registry.py.

Every fault MUST be reversible (saboteur_containment_contract.py enforces this on the
metadata). Fasa 1 = skeleton: the real reset mechanism is wired in Fasa 4 alongside the first
live drill; until then this refuses to act, same as inject.py.
"""

from __future__ import annotations

import sys

from registry import FAULTS


def reset(fault_name: str) -> None:
    matches = [f for f in FAULTS if f.name == fault_name]
    if not matches:
        raise ValueError(f"unknown fault: {fault_name!r} — see simulation/faults/registry.py")
    fault = matches[0]
    if not fault.reversible:
        raise RuntimeError(f"fault {fault_name!r} has no declared reversible reset — containment violation")
    raise NotImplementedError("Fasa 4: wire the real reset mechanism here")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python reset.py <fault_name>")
    reset(sys.argv[1])
