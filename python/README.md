# Python Tooling

Utilities in this folder interact with the ClickHouse instance provisioned through Docker Compose. They cover table initialization, data loading, vector queries, and S3-backed access patterns.

## Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r python/requirements.txt
   ```
3. Copy `.env.example` to `.env` at the repository root and adjust credentials and paths as needed.
4. Download embedding models locally:
   ```powershell
   python python/scripts/download_models.py
   ```
5. Generate the vector dataset using the active embedding model (re-run after switching models):
   ```powershell
   python python/scripts/generate_vector_dataset.py --overwrite
   ```
6. Bootstrap ClickHouse schemas and stage demo datasets:
   ```powershell
   python python/scripts/bootstrap_clickhouse.py
   ```
7. (Optional) Run the CRUD walkthrough from the console:
   ```powershell
   python python/scripts/demo_crud.py
   ```

## Scripts

- `python/scripts/bootstrap_clickhouse.py` – Creates tables, loads dummy data, uploads the S3 dataset, and wires the mapped table.
- `python/scripts/demo_crud.py` – Runs a read-only walkthrough across tabular, vector, and S3-backed data.
- `python/scripts/download_models.py` – Fetches embedding checkpoints from Hugging Face into `assets/models/`.
- `python/scripts/generate_vector_dataset.py` – Produces `assets/data/vector_items.jsonl` by embedding dummy text with the active model.

## Using the Dockerized Jupyter Environment

- Start the stack with Docker Compose and open `http://localhost:8888/lab?token=<JUPYTER_TOKEN>` (defaults to `clickhouse`).
- The notebook image pre-installs `python/requirements.txt`, so `notebooks/warehouse_demo.ipynb` can run immediately.
- Notebook edits persist back to the repository thanks to the shared volume at `/home/jovyan/work`.

Each script reads configuration from `.env`. Update `ACTIVE_EMBEDDING_MODEL` to switch the vector backend.
