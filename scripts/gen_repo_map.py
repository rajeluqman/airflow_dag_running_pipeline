#!/usr/bin/env python3
"""Repo-map generator — the NAVIGATION half of the ANTI-SHORTCUT PROTOCOL (see CLAUDE.md §3).

Ported from CIL (architecture/control_plane_lab/_source_to_port/gen_repo_map.py), philosophy
only: roles/paths are rewritten for this repo's actual layout (no dbt models/seeds/Great
Expectations — this repo models no data, see CLAUDE.md §2), and the dead .sql/.csv handling
from the CIL original was dropped rather than kept as inert content.

None of the other gates answer the cheap question "what is this file, what uses it, what does
it use?" without scanning the repo by hand — and hand-scanning from in-context memory is exactly
the shortcut that produces "missing gaps". This builds a pointer index so the answer is one
cheap read, NOT a whole-repo token burn.

Design rule (the thing that makes it safe): the map is a POINTER, never a substitute for
reading the file. It tells you WHICH file to open; you still read that file fresh before you
touch or assert about it. A pointer you trust without opening is just a bigger stale cache —
the bug, scaled up. So the map is kept *impossible to drift*:

  - It is 100% DERIVED, nothing is hand-authored. Purpose is extracted from the file itself
    (module docstring / first Markdown heading / leading comment), so it lives where it can't
    fall out of sync. Edges are parsed with `ast` (.py imports), not guessed.
  - The CI gate is `--check`: regenerate in memory, diff against the committed REPO_MAP.md,
    fail if they differ (same idea as `black --check` / `gofmt -l`).

Import-edge resolution note (adaptation beyond a straight CIL port): this repo's DAGs and tests
use sys.path tricks (e.g. `from connections.connection_ids import X` inside airflow/dags/*.py,
which works because each DAG inserts `airflow/` onto sys.path) — a dotted import's FIRST
segment alone doesn't always resolve to a local file stem the way it does in a flat layout. So
`py_deps` checks both the first and last dotted segment against local file stems. This is a
heuristic for a navigation aid, not a correctness gate — it can occasionally over-match if two
unrelated files share a stem; read the file to confirm, same as any other map entry.

Stdlib only ($0, no deps). Exit 0 = map is fresh. Exit 1 (with --check) = stale, regenerate.

Run:  python scripts/gen_repo_map.py            # (re)write architecture/REPO_MAP.md
      python scripts/gen_repo_map.py --check    # CI gate: fail if committed map is stale
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAP_PATH = REPO / "architecture" / "REPO_MAP.md"

# Deliberately NOT mapped — config/settings noise where an entry adds nothing. Stated here so
# the exclusion is a decision on the record (cf. "Enumerate, don't sample": name what you leave out).
EXCLUDE = {
    ".gitignore",
    ".claude/settings.json",
    "architecture/REPO_MAP.md",  # the map never maps itself (would self-churn)
}
EXCLUDE_PREFIX = (".github/",)

# Section render order + human label. Anything unmapped-by-role falls through to "other".
ROLE_LABELS = [
    ("planning", "Fasa-0 planning (build authority — Opus)"),
    ("adr", "Architecture Decision Records"),
    ("arch-doc", "Architecture docs (record)"),
    ("dag", "Airflow DAGs (trigger-only)"),
    ("connection", "Connections / secrets-backend indirection"),
    ("fault", "Saboteur faults (staging-only)"),
    ("runbook", "Incident runbooks"),
    ("simulation-doc", "Simulation / chaos-range docs"),
    ("script", "Scripts"),
    ("test", "Tests / contracts"),
    ("hook", "Governance hooks"),
    ("agent", "Cabinet agents"),
    ("confluence", "Confluence sync + onboarding"),
    ("observability", "Observability"),
    ("learning", "Learning"),
    ("config", "Config"),
    ("doc", "Top-level docs"),
    ("other", "Other"),
]


def working_set() -> list[Path]:
    """The repo as it is NOW: tracked + untracked-not-ignored, minus the stated EXCLUDE set."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    files = []
    for raw in out.splitlines():
        rel = raw.strip()
        if not rel or rel in EXCLUDE or rel.startswith(EXCLUDE_PREFIX):
            continue
        if (REPO / rel).is_file():
            files.append(Path(rel))
    return sorted(files, key=lambda p: p.as_posix())


def role_of(rel: str) -> str:
    if rel.startswith("architecture/control_plane_lab/"):
        return "planning"
    if rel.startswith("architecture/ADR/"):
        return "adr"
    if rel.startswith("architecture/"):
        return "arch-doc"
    if rel.startswith("airflow/dags/"):
        return "dag"
    if rel.startswith("airflow/connections/"):
        return "connection"
    if rel.startswith("simulation/faults/"):
        return "fault"
    if rel.startswith("simulation/runbooks/"):
        return "runbook"
    if rel.startswith("simulation/"):
        return "simulation-doc" if Path(rel).suffix == ".md" else "script"
    if rel.startswith("scripts/"):
        return "script"
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith(".claude/hooks/"):
        return "hook"
    if rel.startswith(".claude/agents/"):
        return "agent"
    if rel.startswith("confluence/"):
        return "confluence"
    if rel.startswith("observability/"):
        return "observability"
    if rel.startswith("learning/"):
        return "learning"
    suf = Path(rel).suffix
    if suf == ".md":
        return "doc"
    if suf in (".yml", ".yaml", ".json"):
        return "config"
    if suf == ".sh":
        return "script"
    return "other"


def _clean(text: str, limit: int = 110) -> str:
    """Plain-text, single-line, table-safe. Strip markdown that could confuse downstream gates
    (backticks/links/pipes) so an extracted heading can't masquerade as a real doc reference."""
    text = text.replace("`", "").replace("|", "/")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def purpose_of(path: Path) -> str:
    """Extract the file's own one-line statement of intent — never authored here."""
    suf = path.suffix
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "—"

    if suf == ".py":
        try:
            doc = ast.get_docstring(ast.parse(text))
        except SyntaxError:
            doc = None
        if doc:
            return _clean(doc.strip().splitlines()[0])
        return "(no module docstring)"

    if suf == ".md":
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                return _clean(s.lstrip("#").strip())
            if s and not s.startswith(("<!--", ">", "---")):
                return _clean(s)
        return "—"

    if suf in (".yml", ".yaml"):
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                return _clean(s.lstrip("#").strip())
            if s:
                break
        return "—"

    return "—"


def py_deps(path: Path, local_py: dict[str, str]) -> set[str]:
    """Cross-file LOCAL imports only, via AST. Checks both the first and last dotted segment
    of an `ImportFrom` module against local file stems (see module docstring's adaptation note)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return set()
    deps: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                top = n.name.split(".")[0]
                if top in local_py:
                    deps.add(local_py[top])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                parts = node.module.split(".")
                hit = local_py.get(parts[0]) or local_py.get(parts[-1])
                if hit:
                    deps.add(hit)
    return deps


def build_edges(files: list[Path]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return (uses, used_by) keyed by rel-path. Edges derived from ground truth, not memory."""
    local_py = {p.stem: p.as_posix() for p in files if p.suffix == ".py"}
    uses: dict[str, set[str]] = {p.as_posix(): set() for p in files}
    for p in files:
        rel = p.as_posix()
        if p.suffix == ".py":
            uses[rel] |= py_deps(p, local_py)
        uses[rel].discard(rel)  # never self-edge
    used_by: dict[str, set[str]] = {p.as_posix(): set() for p in files}
    for rel, targets in uses.items():
        for t in targets:
            used_by.setdefault(t, set()).add(rel)
    return uses, used_by


def _names(rels: set[str]) -> str:
    return ", ".join(sorted(Path(r).name for r in rels)) if rels else "—"


def render(files: list[Path]) -> str:
    uses, used_by = build_edges(files)
    by_role: dict[str, list[Path]] = {}
    for p in files:
        by_role.setdefault(role_of(p.as_posix()), []).append(p)

    lines: list[str] = [
        "# REPO_MAP — generated navigation index",
        "",
        "> **GENERATED — do not hand-edit.** `python scripts/gen_repo_map.py` rebuilds it from",
        "> ground truth; CI runs `--check` and fails if this file is stale. Purpose is extracted",
        "> from each file's own docstring / first heading / leading comment; *Uses* and *Used by*",
        "> are parsed (`ast` for Python), never authored.",
        ">",
        "> **This is a pointer, not a cache.** It tells you which file to open — then READ THAT",
        "> FILE FRESH before you edit or assert about it (ANTI-SHORTCUT PROTOCOL, CLAUDE.md §3). A",
        "> pointer trusted without opening the file is just a bigger stale cache.",
        ">",
        "> Not mapped (by design): `.github/`, `.gitignore`, `.claude/settings.json`.",
        "",
        f"**{len(files)} files mapped.**",
        "",
    ]

    for role, label in ROLE_LABELS:
        group = sorted(by_role.get(role, []), key=lambda p: p.as_posix())
        if not group:
            continue
        lines += [f"## {label}", "", "| File | Purpose | Uses | Used by |", "|------|---------|------|---------|"]
        for p in group:
            rel = p.as_posix()
            lines.append(
                f"| `{rel}` | {purpose_of(p)} | {_names(uses.get(rel, set()))} "
                f"| {_names(used_by.get(rel, set()))} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    files = working_set()
    content = render(files)

    if "--check" in argv[1:]:
        if not MAP_PATH.exists():
            print("REPO-MAP: architecture/REPO_MAP.md missing — run python scripts/gen_repo_map.py")
            return 1
        current = MAP_PATH.read_text(encoding="utf-8")
        if current != content:
            new = content.splitlines()
            old = current.splitlines()
            for i in range(max(len(new), len(old))):
                a = old[i] if i < len(old) else "<EOF>"
                b = new[i] if i < len(new) else "<EOF>"
                if a != b:
                    print("REPO-MAP: STALE — committed index does not match ground truth.")
                    print(f"  first divergence at line {i + 1}:")
                    print(f"    committed: {a}")
                    print(f"    expected:  {b}")
                    break
            print("\nRegenerate: python scripts/gen_repo_map.py")
            return 1
        print(f"REPO-MAP: OK — {len(files)} files, index matches ground truth.")
        return 0

    MAP_PATH.write_text(content, encoding="utf-8")
    print(f"REPO-MAP: wrote {MAP_PATH.relative_to(REPO)} — {len(files)} files mapped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
