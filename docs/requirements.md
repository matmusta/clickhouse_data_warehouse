ClickHouse Warehouse Requirements
=================================

Functional Requirements
-----------------------

- **Docker-based deployment**: Provide a reproducible Docker Compose stack that launches ClickHouse services with persistent volumes and optional configuration overrides.
- **Tabular storage**: Define at least one canonical MergeTree table to demonstrate standard structured analytics patterns, including CRUD operations via Python clients.
- **S3-backed storage**: Configure ClickHouse to read and write datasets stored in an external S3-compatible bucket using the `s3` table function or `ENGINE = S3`, with all data exchanges initiated by Python tooling (no third-party integrations required).
- **Vector storage**: Enable ClickHouse vector columns with appropriate indexes (e.g., `INDEX hnsw`) to support similarity search scenarios. Implement end-to-end CRUD-style workflows through Python tooling and generate the vector dataset via the dedicated embedding script.
- **Unified Python tooling**: Ship Python scripts and optional notebooks that can switch between the three storage styles using a shared connection configuration and manage S3 operations end-to-end, including bootstrap and demonstration utilities.
- **Jupyter-based exploration**: Provide a Dockerized Jupyter Notebook environment with project dependencies preinstalled so analysts can run CRUD workflows interactively without touching the host Python setup.
- **Embedded model assets**: Package locally cached Hugging Face embedding models in the repository to power vector workloads without external downloads at runtime, starting with `BAAI/bge-base-en-v1.5` and `Alibaba-NLP/gte-Qwen2-1.5B-instruct`.
- **Observability hooks**: Expose ClickHouse system tables or queries (e.g., `system.query_log`) through Python helpers to validate that operations executed as expected.

Non-functional Requirements
---------------------------

- **ClickHouse-first**: Avoid introducing additional databases or orchestration layers. Supporting services should remain limited to core ClickHouse images and Python tooling.
- **Environment isolation**: Support local development without modifying the host beyond Docker volumes and `.env` files.
- **Security**: Store credentials exclusively in environment files or Docker secrets; never hard-code access keys.
- **Performance validation**: Provide representative dataset sizes and benchmark queries (where feasible) to confirm vector indexes and S3 interactions behave within acceptable latency bounds.
- **Extensibility**: Structure the repository so that new ClickHouse storage patterns (e.g., materialized views, projections) can be added without rewriting the core infrastructure, including the ability to swap or update bundled model assets and toggle between multiple embedding models.
- **Offline readiness**: Ensure the repository contains dummy datasets and the selected embedding models so the environment can run fully offline once cloned, accounting for storage footprint and Git LFS usage if necessary.
- **Documentation**: Maintain up-to-date runbooks covering configuration, deployment, and validation workflows.

Assumptions
-----------

- Developers have access to an S3-compatible bucket with credentials suitable for ClickHouse `s3` integration, which will be consumed exclusively through repository Python tooling.
- Docker Desktop is configured to allocate sufficient memory (>= 4 GB) for ClickHouse workloads.
- Python developers will rely on `clickhouse-connect` or `clickhouse-driver` for client interactions.

Open Questions
--------------

- Confirm the Hugging Face model selections (`BAAI/bge-base-en-v1.5`, `Alibaba-NLP/gte-Qwen2-1.5B-instruct`) remain license-compatible and practical to store in-repo; assess Git LFS adoption for larger checkpoints.
