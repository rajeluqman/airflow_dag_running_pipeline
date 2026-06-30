# Repo Registry — the 5 pipelines this control plane orchestrates

> The 5 pipelines below are the universe (`architecture/control_plane_lab/01_OPUS_DECISIONS.md
> §REJECTED`: "Building NEW pipelines here. The 5 are the universe."). This repo never grows a
> 6th pipeline and never homogenizes these 4 stacks into one interface — each pipeline keeps its
> own stack, this repo only triggers it.

| Pipeline | Compute target | Trigger operator | Connection ID (`airflow/connections/connection_ids.py`) | Cloud environment(s) |
|---|---|---|---|---|
| CIL | DuckDB (dev) → Snowflake (prod compute) | `BashOperator` (bash/python trigger) | `SNOWFLAKE_CIL` | staging + prod (Snowflake) |
| home-credit | AWS Glue (PySpark) | `GlueJobOperator` | `GLUE_HOME_CREDIT` | staging + prod (AWS) |
| olist | Azure Databricks (ADLS) | `DatabricksRunNowOperator` | `DATABRICKS_OLIST` | staging + prod (Azure/Databricks) |
| paysim | Databricks SQL / PySpark+Delta | `DatabricksRunNowOperator` | `DATABRICKS_PAYSIM` | staging + prod (Databricks) |
| Volve | Databricks + MLflow | `DatabricksSubmitRunOperator` | `DATABRICKS_VOLVE` | staging + prod (Databricks) |

## Why heterogeneous, not homogenized

Each pipeline's stack was chosen by that pipeline's own repo for reasons specific to its data and
workload (Glue for home-credit's PySpark batch job, Databricks+Delta for paysim's streaming-
shaped workload, Databricks+MLflow for Volve's model training, Snowflake for CIL's warehouse-
style marts). Forcing all 5 onto one stack here would mean re-deciding compute choices this repo
has no standing to re-decide — `@platform-architect` owns cross-stack *orchestration* design
(how triggers fit together, how staging/prod promotion works across all 5), never each
pipeline's own compute choice.

## Where each pipeline's own logic lives

Nowhere in this repo. `architecture/CROSS_STACK_CONTRACT.md` is the enforced boundary: this repo
never imports, copies, or re-implements any of the 5 repos' transform logic. The pipeline repo
names appear here only as registry metadata (which stack, which connection, which operator) —
this table is intentionally the full extent of what this repo knows about each pipeline's
internals.

## Status (Fasa 1)

All 5 trigger DAGs exist as stubs (`airflow/dags/*.py`) — operator + connection reference only,
real job/run IDs marked `# TODO Fasa 2`. No cloud is provisioned yet; no DAG has actually
triggered a real job. That begins at Fasa 2 (home-credit's Glue job is the first real trigger,
per `architecture/control_plane_lab/02_SONNET_BUILD_KICKOFF.md`'s closing note).
