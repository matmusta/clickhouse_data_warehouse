from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from .clickhouse import client_session
from .config import AppConfig, load_config
from .datasets import load_tabular_events

TABULAR_TABLE = "events"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABULAR_TABLE} (
    event_id UInt32,
    event_time DateTime('UTC'),
    customer_id UInt32,
    event_type LowCardinality(String),
    amount Decimal(10, 2)
) ENGINE = MergeTree
ORDER BY (event_time, event_id)
"""


def ensure_table(*, config: Optional[AppConfig] = None) -> None:
    cfg = config or load_config()
    with client_session(cfg) as client:
        client.execute(CREATE_TABLE_SQL)


def load_sample_data(*, config: Optional[AppConfig] = None) -> int:
    cfg = config or load_config()
    df = load_tabular_events(config=cfg)
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    rows = [
        (
            int(row.event_id),
            row.event_time.to_pydatetime(),
            int(row.customer_id),
            str(row.event_type),
            float(row.amount),
        )
        for row in df.itertuples(index=False)
    ]

    with client_session(cfg) as client:
        client.execute(f"TRUNCATE TABLE IF EXISTS {TABULAR_TABLE}")
        client.execute(
            f"INSERT INTO {TABULAR_TABLE} (event_id, event_time, customer_id, event_type, amount) VALUES",
            rows,
        )
    return len(rows)


def fetch_events(*, limit: int = 20, config: Optional[AppConfig] = None) -> Iterable[tuple]:
    cfg = config or load_config()
    with client_session(cfg) as client:
        return client.execute(
            f"SELECT event_id, event_time, customer_id, event_type, amount FROM {TABULAR_TABLE} ORDER BY event_time DESC LIMIT %(limit)s",
            {"limit": limit},
        )
