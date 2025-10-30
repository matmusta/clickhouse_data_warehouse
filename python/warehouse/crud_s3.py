from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional
import tempfile

from .clickhouse import client_session
from .config import AppConfig, load_config
from .datasets import load_tabular_events
from .s3_utils import ensure_bucket_exists, upload_file

S3_EVENTS_KEY = "datasets/tabular_events.csv"


def stage_sample_dataset(*, config: Optional[AppConfig] = None) -> str:
    cfg = config or load_config()
    ensure_bucket_exists(config=cfg)

    df = load_tabular_events(config=cfg)
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
        temp_path = Path(tmp.name)
        df.to_csv(temp_path, index=False)

    upload_file(temp_path, S3_EVENTS_KEY, config=cfg)
    temp_path.unlink(missing_ok=True)
    return S3_EVENTS_KEY


def _build_s3_url(key: str, cfg: AppConfig) -> str:
    base = cfg.s3.endpoint_url.rstrip("/")
    return f"{base}/{cfg.s3.bucket}/{key}"


def query_s3_dataset(*, config: Optional[AppConfig] = None) -> Iterable[tuple]:
    cfg = config or load_config()
    url = _build_s3_url(S3_EVENTS_KEY, cfg)

    with client_session(cfg) as client:
        return client.execute(
            f"SELECT * FROM s3('{url}', '{cfg.s3.access_key}', '{cfg.s3.secret_key}', 'CSVWithNames')"
        )


def create_s3_mapped_table(*, table_name: str = "s3_events", config: Optional[AppConfig] = None) -> None:
    cfg = config or load_config()
    url = _build_s3_url("datasets/events_*.csv", cfg)
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        event_id UInt32,
        event_time DateTime('UTC'),
        customer_id UInt32,
        event_type String,
        amount Decimal(10, 2)
    ) ENGINE = S3('{url}', '{cfg.s3.access_key}', '{cfg.s3.secret_key}', 'CSVWithNames')
    """

    with client_session(cfg) as client:
        client.execute(ddl)
