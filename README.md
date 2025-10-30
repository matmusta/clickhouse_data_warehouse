ClickHouse Data Warehouse Starter
=================================

This repository scaffolds a ClickHouse-only analytics environment backed by Docker Compose and exercised through Python tooling. The goal is to stand up a consolidated warehouse that supports three primary storage paradigms within ClickHouse:

- Traditional tabular tables for structured analytics workloads.
- Object-backed tables that leverage the ClickHouse `s3` table function for lake-style data stored in S3-compatible buckets.
- Vector indexes for similarity search use cases powered by ClickHouse's native vector capabilities.

Project Layout
--------------

- `docs/requirements.md` – functional and non-functional expectations for the warehouse.
- `docs/system-architecture.md` – planned service topology, storage configuration, and data flow.
- `docs/workflows.md` – operational runbooks for provisioning, ingesting data, and validating CRUD paths.
- `compose/` – Docker Compose definitions for ClickHouse services and supporting configuration.
- `python/` – Python scripts and optional Jupyter notebooks for CRUD validation across table, S3, and vector workloads.
- `assets/` – Versioned dummy datasets and bundled Hugging Face embedding models (`BAAI/bge-base-en-v1.5`, `Alibaba-NLP/gte-Qwen2-1.5B-instruct`) for offline use.
- `storage/` – Host-mounted volumes for ClickHouse data and logs when running the Docker stack.
- `notebooks/` – Jupyter notebooks (e.g., `warehouse_demo.ipynb`) for interactive CRUD demonstrations.

Prerequisites
-------------

- Docker Desktop (with Compose v2) installed and running.
- Python 3.11+ available locally for authoring and running validation scripts.
- A Dockerized [SeaweedFS](https://github.com/seaweedfs/seaweedfs) service is bundled with the stack and exposes an S3-compatible endpoint; no external object store is required unless you override the defaults in `.env`.
- Git LFS configured locally to version large Hugging Face checkpoints stored under `assets/models/`.

Getting Started
---------------

1. Review the documentation under `docs/` to understand the design targets.
2. Review `.env` and adjust values as needed (defaults point ClickHouse and the Python utilities at the bundled SeaweedFS instance). If you change the S3 access keys, mirror the update in `compose/seaweedfs/config.json` so the gateway accepts the new credentials.
3. Launch the stack: `docker compose -f compose/docker-compose.yml up -d`.
4. Create and activate a Python virtual environment, then install dependencies:
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r python/requirements.txt
	```
5. Download embedding checkpoints (uses `.env` paths):
	```powershell
	python python/scripts/download_models.py
	```
6. Generate the vector dataset aligned with the active model (rerun after switching models):
	```powershell
	python python/scripts/generate_vector_dataset.py --overwrite
	```
7. Initialize schemas, load dummy data, and stage S3 assets (this also provisions the SeaweedFS bucket on first run):
	```powershell
	python python/scripts/bootstrap_clickhouse.py
	```
8. Validate CRUD scenarios (tabular, vector, S3) with the walkthrough script:
	```powershell
	python python/scripts/demo_crud.py
	```

Jupyter Notebook Access
-----------------------

- The Compose stack builds and runs a `clickhouse-jupyter` service based on `jupyter/minimal-notebook` with project dependencies preinstalled.
- Default access URL: `http://localhost:8888/lab?token=<JUPYTER_TOKEN>` (token defaults to `clickhouse`, configurable via `.env`).
- Repository content is mounted into `/home/jovyan/work`; notebooks reside in `notebooks/` (see `notebooks/warehouse_demo.ipynb`).
- Use the notebook to run the same bootstrap and CRUD flows interactively if you prefer not to work in the local virtual environment.

Notebook Highlights
-------------------

- `notebooks/warehouse_demo.ipynb` mirrors the CLI utilities in an interactive flow: it validates connectivity, seeds tabular data, materializes embeddings, and now includes a helper that embeds any free-form phrase (for example, Treasury/Tax/Travel scenarios) before querying the ClickHouse ANN index. The output DataFrames make it easy to verify how the warehouse responds to tailored prompts.
- `notebooks/similarity_benchmark.ipynb` synthesizes a larger catalog and benchmarks multiple HNSW configurations. The notebook documents the recall calculation (exact cosine search vs. ANN results) and summarizes latency/recall trade-offs so you can choose appropriate values for `ef_search`, `m`, and `ef_construction`.

Roadmap
-------

- Author Docker Compose manifests under `compose/` to launch a ClickHouse server with persistent storage.
- Configure ClickHouse object storage settings (as needed) while routing all S3 data movement through Python utilities.
- Implement reference tables illustrating tabular, S3-backed, and vector workloads populated with bundled dummy datasets.
- Deliver Python-based test harnesses (scripts and notebooks) that exercise CRUD operations across the three storage modalities and ship local Hugging Face embedding models stored within the repository, with a simple switch to choose between `BAAI/bge-base-en-v1.5` and `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (extensible to more in the future).
- Evaluate adding automated regression tests (pytest or notebooks) to exercise bootstrap and CRUD scripts.

Contributing
------------

Please open issues or pull requests for proposed improvements. Keep contributions focused on ClickHouse and Python tooling in line with the scope described above.
