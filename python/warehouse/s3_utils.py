from __future__ import annotations

from pathlib import Path
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .config import AppConfig, load_config


def build_s3_client(config: Optional[AppConfig] = None) -> BaseClient:
    cfg = config or load_config()
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=cfg.s3.endpoint_url,
        region_name=cfg.s3.region,
        aws_access_key_id=cfg.s3.access_key,
        aws_secret_access_key=cfg.s3.secret_key,
    )


def ensure_bucket_exists(client: Optional[BaseClient] = None, *, config: Optional[AppConfig] = None) -> None:
    cfg = config or load_config()
    s3 = client or build_s3_client(cfg)
    try:
        s3.head_bucket(Bucket=cfg.s3.bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"404", "NoSuchBucket"}:
            s3.create_bucket(Bucket=cfg.s3.bucket)
        elif error_code in {"403", "AccessDenied"}:
            raise PermissionError("Insufficient permissions to access S3 bucket") from exc
        else:
            raise


def upload_file(source: Path, key: str, *, client: Optional[BaseClient] = None, config: Optional[AppConfig] = None) -> None:
    cfg = config or load_config()
    if not source.exists():
        raise FileNotFoundError(f"Local file not found: {source}")

    s3 = client or build_s3_client(cfg)
    s3.upload_file(str(source), cfg.s3.bucket, key)


def list_objects(prefix: str = "", *, client: Optional[BaseClient] = None, config: Optional[AppConfig] = None) -> list[str]:
    cfg = config or load_config()
    s3 = client or build_s3_client(cfg)
    paginator = s3.get_paginator("list_objects_v2")
    items: list[str] = []

    for page in paginator.paginate(Bucket=cfg.s3.bucket, Prefix=prefix):
        contents = page.get("Contents", [])
        for entry in contents:
            key = entry.get("Key")
            if key:
                items.append(key)

    return items
