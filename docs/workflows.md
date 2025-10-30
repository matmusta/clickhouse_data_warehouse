Workflows
=========

Environment Provisioning
------------------------

1. Copy `.env.example` to `.env` (to be added) and populate ClickHouse admin credentials, S3 endpoint, and access keys.
2. Run `docker compose up -d` from the repository root once the Compose files are available.
3. Verify the server is reachable: `docker compose exec clickhouse-server clickhouse-client --query "SELECT version()"`.
4. Download embedding checkpoints: `python python/scripts/download_models.py`.
5. Generate the vector dataset: `python python/scripts/generate_vector_dataset.py --overwrite`.
6. Execute `python python/scripts/bootstrap_clickhouse.py` to initialize schemas, load dummy datasets, and stage the S3 assets.
7. Access the notebook service at `http://localhost:8888/lab?token=<JUPYTER_TOKEN>` for interactive exploration (token defaults to `clickhouse`).

Schema Bootstrapping
--------------------

1. Apply base schema SQL via Docker `clickhouse-client` or Python bootstrap script.
2. Create MergeTree tables for structured analytics workloads.
3. Use Python utilities to upload dummy datasets to the configured S3 bucket, then define S3-backed tables referencing the uploaded objects and verify schema metadata with `DESCRIBE TABLE`.
4. Create vector tables with appropriate `Vector` column definitions and secondary indexes (e.g., `INDEX hnsw_vec hnsw(vector_column, 'DIM=1536, M=16, EF_SEARCH=200') TYPE hnsw GRANULARITY 1`).

Python CRUD Validation
----------------------

- **Tabular**: Use `clickhouse-driver` to run parameterized `INSERT`, `SELECT`, `UPDATE` (mutations), and `DELETE` (table-level delete) operations. Validate row counts before and after operations.
- **S3-backed**: Use Python to stage objects in S3, then trigger `INSERT INTO s3_table SELECT ...` and `SELECT * FROM s3_table LIMIT ...` queries to confirm round-trip access. Include error handling for missing objects.
- **Vector**: Insert embeddings, execute similarity search (`ORDER BY distance(vector_column, :query_vector)`) and validate mutation behavior (delete and reinsert test vectors).

Data Management
---------------

- Maintain dummy datasets and the downloaded Hugging Face embedding models (`BAAI/bge-base-en-v1.5`, `Alibaba-NLP/gte-Qwen2-1.5B-instruct`) under `assets/` so runs remain deterministic, offline-capable, and easy to switch between.
- Use the `python/scripts/bootstrap_clickhouse.py` helper to reload tabular/vector tables and restage S3 artifacts when needed.
- Regenerate `assets/data/vector_items.jsonl` with `python/scripts/generate_vector_dataset.py` whenever switching embedding models or modifying dummy narratives.
- Leverage `notebooks/warehouse_demo.ipynb` inside the Jupyter container to execute CRUD flows cell-by-cell without leaving the browser.
- Additional custom loaders can live alongside `python/scripts/demo_crud.py` for scenario-specific testing.
- Use ClickHouse's `ALTER TABLE ... UPDATE` or `DELETE` statements for maintenance tasks.
- Store canonical datasets (CSV, Parquet) under a dedicated `data/` directory (planned) for repeatable ingestion.

Observability & QA
------------------

- Query `system.query_log` via Python to confirm CRUD executions and capture latency metrics.
- Leverage `system.parts` to monitor MergeTree part counts and ensure merges behave as expected.
- Automated tests are out of scope for the initial development iteration; rely on manual notebook/script verification such as `python/scripts/demo_crud.py` or the bundled Jupyter notebook walkthrough.

Rollback & Cleanup
------------------

- To reset local state, stop containers (`docker compose down`) and remove volumes if necessary (`docker compose down --volumes`).
- Ensure S3 buckets are cleaned manually or through Python cleanup scripts after test runs.
- Version control changes to configuration and SQL artifacts to maintain auditability.
