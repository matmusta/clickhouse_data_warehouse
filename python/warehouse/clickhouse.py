from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable, Optional

from clickhouse_driver import Client

from .config import AppConfig, load_config


def build_client(config: Optional[AppConfig] = None) -> Client:
    cfg = config or load_config()
    return Client(
        host=cfg.clickhouse.host,
        port=cfg.clickhouse.native_port,
        user=cfg.clickhouse.user,
        password=cfg.clickhouse.password,
        database=cfg.clickhouse.database,
        secure=False,
        compression=True,
        send_receive_timeout=30,
    )


@contextmanager
def client_session(config: Optional[AppConfig] = None):
    client = build_client(config)
    try:
        yield client
    finally:
        client.disconnect()


def execute(query: str, params: Optional[dict[str, Any]] = None, *, config: Optional[AppConfig] = None) -> Iterable[Any]:
    with client_session(config) as client:
        return client.execute(query, params or {})
