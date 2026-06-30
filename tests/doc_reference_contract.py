#!/usr/bin/env python3
"""Doc-reference contract — deterministic gate against documentation drift.

Ported from CIL (architecture/control_plane_lab/_source_to_port/doc_reference_contract.py),
philosophy-only per the porting rule (CLAUDE.md §2): this repo models no data, so the original
C1 check (dbt model/seed token existence) is DROPPED entirely rather than kept as a dead/inert
check — there is nothing in this repo shaped like `fact_x`/`dim_y` and there never will be. Only
C2 (repo-path existence) is ported, with PATH_ROOTS adapted to this repo's actual top-level
layout.

This is the ANTI-SHORTCUT PROTOCOL's machine half (CLAUDE.md §3): proves every repo path an
architecture doc references in backticks or a `[]()` link actually exists on disk. Code does not
get tired, and code does not write a stale path from memory the way an author under pressure
might.

What it checks (deliberately narrow, to keep false positives near zero):
  C2  PATH refs — backtick tokens and []() link targets that point at a repo path under one of
      PATH_ROOTS must exist on disk.

What it deliberately does NOT check: prose mentions outside backticks (too noisy); external
URLs; `s3://`/cloud-ARN runtime paths (not yet relevant — no live cloud in Fasa 1).

Stdlib only ($0, no deps). Exit 0 = every checked reference resolves. Exit 1 = drift.

Run:  python tests/doc_reference_contract.py                 # default doc set
      python tests/doc_reference_contract.py path/to/FILE.md ...   # explicit files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Repo path roots that must resolve on disk if a doc points at them — adapted for this repo's
# layout (no models/seeds/dbt; adds airflow/, simulation/, learning/, confluence/, observability/).
PATH_ROOTS = (
    "airflow/", "scripts/", "architecture/", "tests/", ".claude/", "simulation/",
    "learning/", "confluence/", "observability/",
)

# Intentionally-not-yet-existing names a doc may legitimately reference, each with a reason so
# the allowlist can't quietly rot into a dumping ground. Empty today — add an entry only with a
# stated reason (mirrors CIL's GRANDFATHERED pattern).
ALLOW: dict[str, str] = {
    "airflow/connections/.env": "gitignored by design (.gitignore '**/connections/*.env') — "
    "real local secrets file, never committed; architecture/SECRETS_BACKEND.md instructs the "
    "reader to create it from airflow/connections/.env.example.",
}


def _default_docs() -> list[Path]:
    """Current-state 'architecture of record' docs: architecture/*.md (top-level) plus
    architecture/ADR/*.md. Deliberately excludes architecture/control_plane_lab/ — those are
    the Fasa-0 planning/build-authority docs (past-tense / future-build-target references are
    valid there, same reasoning CIL applies to SPEC_*.md and changelogs)."""
    docs = sorted((REPO / "architecture").glob("*.md"))
    adr_dir = REPO / "architecture" / "ADR"
    if adr_dir.exists():
        docs += sorted(adr_dir.glob("*.md"))
    return docs


def check(docs: list[Path]) -> list[str]:
    errors: list[str] = []
    backtick = re.compile(r"`([^`]+)`")
    link = re.compile(r"\]\(([^)]+)\)")

    for doc in docs:
        if not doc.exists():
            errors.append(f"{doc}: doc file does not exist")
            continue
        rel = doc.relative_to(REPO)
        for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            candidates = backtick.findall(line) + link.findall(line)
            for cand in candidates:
                cand = cand.strip().split("#", 1)[0].strip()  # drop anchors
                if cand.startswith(("http://", "https://", "s3://", "mailto:")):
                    continue
                if not cand.startswith(PATH_ROOTS):
                    continue
                if "*" in cand or "{" in cand:  # glob / template path — not a literal file
                    continue
                if cand in ALLOW:
                    continue
                if not (REPO / cand).exists():
                    errors.append(f"{rel}:{lineno}  C2 path `{cand}` referenced but not found on disk")

    return errors


def main(argv: list[str]) -> int:
    docs = [Path(a) for a in argv[1:]] if len(argv) > 1 else _default_docs()
    docs = [d if d.is_absolute() else (REPO / d) for d in docs]
    errors = check(docs)
    if errors:
        print(f"DOC-REFERENCE CONTRACT: {len(errors)} drift violation(s)\n")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nFix the doc or add a reasoned entry to ALLOW. Drift is a lie waiting to mislead.")
        return 1
    print(f"DOC-REFERENCE CONTRACT: OK — {len(docs)} doc(s), all path references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
