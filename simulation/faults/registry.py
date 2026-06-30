"""Fault registry — the single source of truth saboteur_containment_contract.py and
cost_guard.py both check against.

Fasa 1 = skeleton only (architecture/control_plane_lab/00_MASTER_SPEC.md §8): every fault below
is PLANNED, not live — `live=False` until `@saboteur` runs the first real drill (Fasa 4+).
inject.py/reset.py refuse to act on a fault while `live=False`.

Every field here is a containment/cost declaration the contracts enforce mechanically, not a
suggestion:
  - environment   MUST be "staging" — this repo's hard safety boundary.
  - blast_radius  plain-language statement of exactly what this fault can touch.
  - prod_credential_refs   MUST be empty — no path from a fault to a prod credential, ever.
  - reversible    MUST be True — every fault needs a working, declared reset.
  - auto_teardown plain-language statement of what gets torn down/suspended after the drill.
  - budget_ceiling_usd   per-drill cost ceiling in USD; must be a positive number.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fault:
    name: str
    environment: str
    blast_radius: str
    prod_credential_refs: tuple[str, ...]
    reversible: bool
    auto_teardown: str
    budget_ceiling_usd: float
    live: bool


FAULTS: tuple[Fault, ...] = (
    Fault(
        name="glue_job_throttle_staging",
        environment="staging",
        blast_radius="home-credit's staging Glue job concurrency setting only — no other "
        "job, no other environment.",
        prod_credential_refs=(),
        reversible=True,
        auto_teardown="restore the original Glue job concurrency setting (reset.py)",
        budget_ceiling_usd=5.0,
        live=False,  # TODO Fasa 4: first real drill
    ),
    Fault(
        name="databricks_cluster_kill_staging",
        environment="staging",
        blast_radius="olist's staging Databricks cluster only (terminate mid-run) — no other "
        "cluster, no other environment.",
        prod_credential_refs=(),
        reversible=True,
        auto_teardown="terminate any cluster the fault spun up; confirm no orphaned cluster "
        "remains running after reset.py",
        budget_ceiling_usd=10.0,
        live=False,  # TODO Fasa 4: first real drill
    ),
)
