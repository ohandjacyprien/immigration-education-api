from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import boto3
from botocore.config import Config
from .settings import settings

@dataclass
class StorageCfg:
    endpoint_url: str
    access_key: str
    secret_key: str
    region: str
    bucket: str
    prefix: str
    expires_sec: int

def get_cfg() -> StorageCfg:
    return StorageCfg(
        endpoint_url=settings.S3_ENDPOINT_URL,
        access_key=settings.S3_ACCESS_KEY_ID,
        secret_key=settings.S3_SECRET_ACCESS_KEY,
        region=settings.S3_REGION,
        bucket=settings.S3_BUCKET,
        prefix=settings.S3_PREFIX,
        expires_sec=settings.S3_SIGNED_URL_EXPIRES_SEC,
    )

def is_configured() -> bool:
    cfg = get_cfg()
    return bool(cfg.endpoint_url and cfg.access_key and cfg.secret_key and cfg.bucket)

def _client():
    cfg = get_cfg()
    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint_url,
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
        region_name=cfg.region,
        config=Config(signature_version="s3v4"),
    )

def presign_get_url(key: str, download_name: Optional[str] = None) -> str:
    cfg = get_cfg()
    s3 = _client()
    params = {"Bucket": cfg.bucket, "Key": key}
    if download_name:
        params["ResponseContentDisposition"] = f'attachment; filename="{download_name}"'
    return s3.generate_presigned_url("get_object", Params=params, ExpiresIn=cfg.expires_sec)
