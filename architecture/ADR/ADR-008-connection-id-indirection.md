# ADR-008 — Connection ID indirection via connection_ids.py

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

Airflow operators take a `conn_id` string argument to look up the connection in the backend. The
naive approach — inline string literals like `aws_conn_id="glue_home_credit"` scattered across
DAG files — creates a maintenance hazard: renaming a connection ID requires grepping all DAG
files, and a mismatch between the string in code and the registered connection name causes a
silent runtime failure (DAG appears to run but the operator can't connect).

## Decision

`airflow/connections/connection_ids.py` is the single source of truth for all symbolic connection
ID constants. Every DAG imports the constant it needs from this module:

```python
from connections.connection_ids import GLUE_HOME_CREDIT
...
aws_conn_id=GLUE_HOME_CREDIT
```

No DAG file contains a connection ID string literal. The module itself is the canonical registry;
the `.env.example` file documents the corresponding `AIRFLOW_CONN_*` environment variable names
for local setup.

## Consequences

- **Positive:** Renaming a connection ID is a one-file change in `connection_ids.py`; all DAGs
  update automatically. The mismatch class of bug is eliminated.
- **Positive:** `tests/cross_stack_contract.py` can verify the indirection is used (checks that
  `connections` is imported in every DAG) rather than relying on code review.
- **Positive:** The module documents which connections exist in the system — a reader can see all
  5 at a glance without grepping DAG files.
- **Requires:** The `sys.path` trick in each DAG file (`sys.path.insert(0, ...)`) so that
  `from connections.connection_ids import X` resolves correctly when Airflow runs the DAG from its
  own import context. This is documented in the module header.

Full doc: `architecture/SECRETS_BACKEND.md` §Python layer.
