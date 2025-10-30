System Architecture
===================

Overview
--------

The environment targets a single-node ClickHouse deployment orchestrated through Docker Compose. Python clients run outside the stack and connect via the native TCP interface or the HTTP REST API. Object storage interactions occur through the ClickHouse `s3` table function pointed at an external S3-compatible bucket, with all S3 requests initiated by Python tooling.

Components
----------

- **ClickHouse Server** (`clickhouse/clickhouse-server`): Core analytical database hosting MergeTree tables, vector indexes, and S3-backed tables.
- **ClickHouse Client Container** (`clickhouse/clickhouse-client`, optional): Provides shell access for administrative tasks and schema bootstrapping.
- **Persistent Volumes**: Bind-mount host directories (e.g., `./storage/clickhouse`) to preserve metadata and table data across container restarts.
- **Python Tooling**: Local scripts/notebooks leveraging the ClickHouse native driver (`clickhouse-driver`) for high-throughput operations and `clickhouse-connect` for ease of use in notebooks. The same tooling manages S3 data transfers and seeds tabular/vector datasets.
- **External S3 Bucket**: S3-compatible storage endpoint (AWS S3, MinIO, or equivalent) accessible via HTTPS. ClickHouse authenticates using access and secret keys supplied through environment variables.
- **Bundled Model & Data Assets**: An `assets/` directory contains dummy datasets and locally cached Hugging Face embedding models (`BAAI/bge-base-en-v1.5`, `Alibaba-NLP/gte-Qwen2-1.5B-instruct`) to keep the stack self-contained and configurable.
- **Docker Compose Manifests**: `compose/docker-compose.yml` encapsulates the ClickHouse server deployment, mounting `compose/config/` into the container for experimental vector features.
- **Jupyter Notebook Service**: A Dockerized Jupyter environment (`clickhouse-jupyter`) built from `jupyter/minimal-notebook` with repository dependencies baked in, exposing port `8888` for interactive exploration.
- **Vector Dataset Generator**: `python/scripts/generate_vector_dataset.py` derives `assets/data/vector_items.jsonl` from dummy narratives using the active embedding model so table schemas match model dimensionality.

Data Domains
------------

- **Tabular Warehouse**: MergeTree tables optimized for large-scale analytic queries.
- **S3 Data Lake**: Semi-structured or cold data stored in object storage, accessed through ClickHouse `ENGINE = S3` or table functions for on-demand ingestion.
- **Vector Store**: High-dimensional vector columns using ClickHouse's `Vector` type and `HNSW` or `IVFFlat` secondary indexes to enable similarity search. Embeddings are generated via the bundled Hugging Face models invoked inside Python workflows, with configuration allowing runtime selection between the supported checkpoints.

Networking
----------

- Publish ClickHouse TCP (`9000`) and HTTP (`8123`) ports to the host for Python clients.
- Restrict access via Docker network policies and, if needed, enable ClickHouse user profiles with IP-based constraints.
- Store S3 credentials in environment variables injected through Compose and avoid committing secrets to version control; Python scripts source these variables when orchestrating uploads/downloads.

Configuration Strategy
----------------------

- Mount a custom configuration directory (`./compose/config/`) into `/etc/clickhouse-server/` for tuning storage policies, user profiles, and S3 disk definitions.
- Define storage policies that route specific tables to the S3-backed disk while keeping vector tables on fast local storage.
- Enable experimental vector functionality (`allow_experimental_object_type`, `allow_experimental_analyzer`) when required by the target ClickHouse version.

Data Flow
---------

1. **Ingestion**: Python scripts push structured dummy data into MergeTree tables via the native driver; bulk loads may leverage `INSERT INTO ... FORMAT Parquet` for efficiency.
2. **Object Storage**: Python tooling stages data in S3 (uploading via SDKs) and issues `CREATE TABLE ... ENGINE = S3` statements so ClickHouse can query the uploaded objects.
3. **Vector Operations**: Embeddings generated with the bundled Hugging Face model (via the dataset generator) are inserted into vector tables. Similarity queries (e.g., `SELECT ... ORDER BY distance(...) LIMIT N`) are executed via Python clients.
4. **Observability**: Admin tooling queries `system.metrics`, `system.query_log`, and `system.tables` to monitor health and usage patterns.

Deployment Lifecycle
--------------------

1. Build environment variables and secrets (`.env`).
2. Launch Docker Compose stack (`docker compose up -d`).
3. Execute `python python/scripts/bootstrap_clickhouse.py` to initialize schemas and stage datasets.
4. Execute CRUD validation flows in Python to confirm table accessibility across storage modes.
5. Tear down or iterate by adjusting configuration under `compose/config/`.
6. Optionally connect to `http://localhost:8888` using the configured token to execute the companion notebook (`notebooks/warehouse_demo.ipynb`).
