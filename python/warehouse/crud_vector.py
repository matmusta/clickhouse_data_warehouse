from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from .clickhouse import client_session
from .config import AppConfig, load_config
from .datasets import VectorRecord, load_vector_items

VECTOR_TABLE = "item_vectors"


def _ensure_records(records: Sequence[VectorRecord]) -> Sequence[VectorRecord]:
    if not records:
        raise ValueError(
            "Vector dataset is empty. Run python/scripts/generate_vector_dataset.py to populate assets/data/vector_items.jsonl."
        )
    return records


def _create_table_sql(dimension: int) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {VECTOR_TABLE} (
        item_id UInt32,
        category LowCardinality(String),
        embedding Array(Float32) CODEC(NONE),
        CONSTRAINT embedding_length CHECK length(embedding) = {dimension},
        INDEX idx_embedding_hnsw embedding TYPE vector_similarity('hnsw', 'cosineDistance', {dimension}) GRANULARITY 1
    ) ENGINE = MergeTree
    ORDER BY item_id
    """


def ensure_table(*, config: Optional[AppConfig] = None, records: Optional[Sequence[VectorRecord]] = None) -> None:
    cfg = config or load_config()
    loaded_records = _ensure_records(records or list(load_vector_items(config=cfg)))
    dimension = len(loaded_records[0].vector)

    with client_session(cfg) as client:
        # Recreate the table to guarantee the schema matches the current embedding dimension.
        client.execute(f"DROP TABLE IF EXISTS {VECTOR_TABLE}")
        client.execute(_create_table_sql(dimension))


def load_sample_vectors(*, config: Optional[AppConfig] = None, records: Optional[Sequence[VectorRecord]] = None) -> int:
    cfg = config or load_config()
    loaded_records = list(records or load_vector_items(config=cfg))
    _ensure_records(loaded_records)
    payload: List[Tuple[int, str, List[float]]] = [
        (rec.item_id, rec.category, rec.vector) for rec in loaded_records
    ]

    with client_session(cfg) as client:
        client.execute(f"TRUNCATE TABLE IF EXISTS {VECTOR_TABLE}")
        client.execute(
            f"INSERT INTO {VECTOR_TABLE} (item_id, category, embedding) VALUES",
            payload,
        )

    return len(payload)


def similarity_search(query_vector: List[float], *, limit: int = 3, config: Optional[AppConfig] = None) -> Iterable[tuple]:
    cfg = config or load_config()
    if not query_vector:
        raise ValueError("Query vector is empty")

    with client_session(cfg) as client:
        return client.execute(
            f"""
            SELECT item_id, category,
                   cosineDistance(embedding, %(query_vector)s) AS score
            FROM {VECTOR_TABLE}
            ORDER BY score ASC
            LIMIT %(limit)s
            """,
            {"query_vector": query_vector, "limit": limit},
        )
