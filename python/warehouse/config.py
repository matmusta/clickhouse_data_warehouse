from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os

# Resolve project root (repository root is two levels above this file)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    # Allow falling back to process environment when .env isn't present
    load_dotenv()


@dataclass(frozen=True)
class ClickHouseSettings:
    host: str
    native_port: int
    http_port: int
    user: str
    password: str
    database: str


@dataclass(frozen=True)
class S3Settings:
    endpoint_url: str
    region: str
    access_key: str
    secret_key: str
    bucket: str


@dataclass(frozen=True)
class ModelSettings:
    primary: str
    secondary: str
    active: str


@dataclass(frozen=True)
class PathSettings:
    assets_dir: Path
    model_cache_dir: Path
    data_dir: Path


@dataclass(frozen=True)
class AppConfig:
    clickhouse: ClickHouseSettings
    s3: S3Settings
    models: ModelSettings
    paths: PathSettings


def _env(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def load_config() -> AppConfig:
    clickhouse = ClickHouseSettings(
        host=_env("CLICKHOUSE_HOST", "localhost"),
        native_port=int(_env("CLICKHOUSE_NATIVE_PORT", "9000")),
        http_port=int(_env("CLICKHOUSE_HTTP_PORT", "8123")),
        user=_env("CLICKHOUSE_USER", "default"),
        password=_env("CLICKHOUSE_PASSWORD", ""),
        database=_env("CLICKHOUSE_DEFAULT_DATABASE", "default"),
    )

    s3 = S3Settings(
        endpoint_url=_env("S3_ENDPOINT"),
        region=_env("S3_REGION", "us-east-1"),
        access_key=_env("S3_ACCESS_KEY"),
        secret_key=_env("S3_SECRET_KEY"),
        bucket=_env("S3_BUCKET"),
    )

    models = ModelSettings(
        primary=_env("EMBEDDING_MODEL_PRIMARY", "BAAI/bge-base-en-v1.5"),
        secondary=_env(
            "EMBEDDING_MODEL_SECONDARY", "Alibaba-NLP/gte-Qwen2-1.5B-instruct"
        ),
        active=_env("ACTIVE_EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"),
    )

    paths = PathSettings(
        assets_dir=(PROJECT_ROOT / _env("ASSETS_DIR", "assets")).resolve(),
        model_cache_dir=(
            PROJECT_ROOT / _env("MODEL_CACHE_DIR", "assets/models")
        ).resolve(),
        data_dir=(PROJECT_ROOT / _env("DATA_DIR", "assets/data")).resolve(),
    )

    return AppConfig(clickhouse=clickhouse, s3=s3, models=models, paths=paths)
