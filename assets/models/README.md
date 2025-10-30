# Model Cache

Download and store embedding checkpoints in this directory so the Python tooling can operate offline. Use the helper script located at `python/scripts/download_models.py` to fetch the following models:

- `BAAI/bge-base-en-v1.5`
- `Alibaba-NLP/gte-Qwen2-1.5B-instruct`

Large binaries should be committed via Git LFS to keep the repository manageable.

After downloading, run `python/python/scripts/generate_vector_dataset.py` to produce `assets/data/vector_items.jsonl` aligned with the active model.
