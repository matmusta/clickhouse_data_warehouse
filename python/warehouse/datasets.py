from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .config import AppConfig, load_config

VECTOR_DATASET_FILENAME = "vector_items.jsonl"


@dataclass(frozen=True)
class VectorRecord:
    item_id: int
    category: str
    vector: List[float]
    text: str | None = None


def _data_path(filename: str, config: AppConfig) -> Path:
    return config.paths.data_dir / filename


def load_tabular_events(*, config: AppConfig | None = None) -> pd.DataFrame:
    cfg = config or load_config()
    path = _data_path("tabular_events.csv", cfg)
    return pd.read_csv(path)


def load_vector_items(*, config: AppConfig | None = None) -> Iterable[VectorRecord]:
    cfg = config or load_config()
    path = _data_path(VECTOR_DATASET_FILENAME, cfg)

    if not path.exists():
        raise FileNotFoundError(
            f"Vector dataset not found at {path}. Run python/scripts/generate_vector_dataset.py first."
        )

    records: list[VectorRecord] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            records.append(
                VectorRecord(
                    item_id=int(payload["item_id"]),
                    category=str(payload["category"]),
                    vector=[float(x) for x in payload["vector"]],
                    text=payload.get("text"),
                )
            )
    return records
