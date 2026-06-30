#!/usr/bin/env python3
"""Cross-stack contract — proves every DAG in this repo is trigger-only.

This is the single most important boundary in the repo (CLAUDE.md §1, §2;
architecture/control_plane_lab/01_OPUS_DECISIONS.md "DAGs are trigger-only"). Business logic
must never enter `airflow/dags/`: it stays in each pipeline's own repo. A DAG file here is an
operator placeholder plus a connection reference, nothing else.

What it checks, per file under airflow/dags/*.py (enumerated explicitly, not sampled):
  1. The 5 expected Fasa-1 stub DAGs all exist — a gate with nothing to check is a dead gate.
  2. No import of a data-transform-shaped module (pyspark/pandas/numpy/duckdb) or of any of the
     5 pipeline repos' own package names — that would mean business logic crossed the boundary.
  3. No SQL statement (SELECT..FROM, INSERT INTO, CREATE TABLE, DROP TABLE, MERGE INTO,
     UPDATE..SET, DELETE FROM) appears anywhere in the file — a trigger has no business
     constructing a query.
  4. No PySpark-shaped transform call (`spark.sql(`, `spark.read`, `.withColumn(`, `.toDF(`,
     `.createDataFrame(`) appears anywhere in the file.
  5. No hardcoded-secret-shaped literal (AWS access key pattern, `password=`/`secret=` string
     literals) — defense in depth alongside the CI committed-secret guard.
  6. The file imports the connection-ID indirection (`connections.connection_ids`) rather than
     inlining a literal connection string — the secrets-backend boundary (architecture/SECRETS_BACKEND.md).
  7. The file carries a `TODO Fasa 2` marker — Fasa 1 stubs must be visibly marked as stubs,
     never silently presented as a finished trigger with a real job ID.

Stdlib only ($0, no deps). Exit 0 = every DAG is trigger-only. Exit 1 = a boundary violation.

Run: python tests/cross_stack_contract.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DAGS_DIR = REPO / "airflow" / "dags"

EXPECTED_DAGS = {
    "cil_dag.py",
    "home_credit_dag.py",
    "olist_dag.py",
    "paysim_dag.py",
    "volve_dag.py",
}

# Module names that would mean a transform body crossed the trigger-only boundary.
DENY_IMPORTS = {"pyspark", "pandas", "numpy", "duckdb", "home_credit", "olist", "paysim", "volve", "cil"}

SQL_PATTERNS = [
    re.compile(r"\bSELECT\b[\s\S]{0,200}?\bFROM\b", re.IGNORECASE),
    re.compile(r"\bINSERT\s+INTO\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+(OR\s+REPLACE\s+)?TABLE\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bMERGE\s+INTO\b", re.IGNORECASE),
    re.compile(r"\bUPDATE\b[\s\S]{0,100}?\bSET\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
]

PYSPARK_CALL_PATTERNS = [
    re.compile(r"spark\.sql\("),
    re.compile(r"spark\.read\b"),
    re.compile(r"\.withColumn\("),
    re.compile(r"\.toDF\("),
    re.compile(r"\.createDataFrame\("),
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)\bpassword\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)\bsecret\s*=\s*['\"][^'\"]+['\"]"),
]

TODO_MARKER = "TODO Fasa 2"


def _imported_top_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                names.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                names.add(node.module.split(".")[0])
    return names


def check_dag_file(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(REPO).as_posix()
    text = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return [f"{rel}: SyntaxError — {e}"]

    imported = _imported_top_names(tree)
    denied_hits = imported & DENY_IMPORTS
    if denied_hits:
        errors.append(f"{rel}: imports business-logic-shaped module(s) {sorted(denied_hits)} — trigger-only violation")

    for pat in SQL_PATTERNS:
        if pat.search(text):
            errors.append(f"{rel}: contains a SQL statement matching /{pat.pattern}/ — trigger-only violation")

    for pat in PYSPARK_CALL_PATTERNS:
        if pat.search(text):
            errors.append(f"{rel}: contains a PySpark-shaped transform call matching /{pat.pattern}/ — trigger-only violation")

    for pat in SECRET_PATTERNS:
        if pat.search(text):
            errors.append(f"{rel}: matches a hardcoded-secret-shaped pattern /{pat.pattern}/")

    if "connections" not in imported:
        errors.append(f"{rel}: does not import the connection_ids indirection (connections.connection_ids) — check for a hardcoded connection reference")

    if TODO_MARKER not in text:
        errors.append(f"{rel}: missing '{TODO_MARKER}' marker — Fasa-1 stubs must be visibly marked as stubs")

    return errors


def check() -> list[str]:
    errors: list[str] = []

    if not DAGS_DIR.exists():
        return ["airflow/dags/ does not exist — no DAGs to check (dead gate)"]

    present = {p.name for p in DAGS_DIR.glob("*.py")}
    missing = EXPECTED_DAGS - present
    if missing:
        errors.append(f"airflow/dags/: missing expected Fasa-1 stub DAG(s): {sorted(missing)}")

    all_dag_files = sorted(DAGS_DIR.glob("*.py"))
    if not all_dag_files:
        errors.append("airflow/dags/: contains no .py files at all — dead gate, nothing to check")

    for path in all_dag_files:
        errors.extend(check_dag_file(path))

    return errors


def main(argv: list[str]) -> int:
    errors = check()
    if errors:
        print(f"CROSS-STACK CONTRACT: {len(errors)} violation(s)\n")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print(f"CROSS-STACK CONTRACT: OK — {len(list(DAGS_DIR.glob('*.py')))} DAG(s) checked, all trigger-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
