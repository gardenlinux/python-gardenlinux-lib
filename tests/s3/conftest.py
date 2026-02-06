# -*- coding: utf-8 -*-

from dataclasses import dataclass
from hashlib import md5, sha256
from io import BytesIO
from pathlib import Path
from typing import Any, Generator

import boto3
import pytest
from moto import mock_aws
from mypy_boto3_s3.service_resource import S3ServiceResource

BUCKET_NAME = "test-bucket"
REGION = "us-east-1"


@dataclass(frozen=True)
class S3Env:
    s3: S3ServiceResource
    bucket_name: str
    tmp_path: Path
    cname: str


def make_cname(
    flavor: str = "container",
    arch: str = "amd64",
    version: str = "1234.1",
    commit: str = "abc123long",
) -> str:
    """
    Helper function to build cname. Can be used to customized the cname.
    """
    return f"{flavor}-{arch}-{version}-{commit[:8]}"


# Helpers to compute digests for fake files
def dummy_digest(data: BytesIO, algo: str) -> Any:
    """
    Dummy for file_digest() to compute hashes for in-memory byte streams
    """
    content = data.read()
    data.seek(0)  # Reset byte cursor to start for multiple uses

    if algo == "md5":
        return md5(content)
    elif algo == "sha256":
        return sha256(content)
    else:
        raise ValueError(f"Unsupported algo: {algo}")


@pytest.fixture(autouse=True)
def s3_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[S3Env, None, None]:
    """
    Provides a clean S3 setup for each test.
    """
    with mock_aws():
        s3 = boto3.resource("s3", region_name=REGION)
        s3.create_bucket(Bucket=BUCKET_NAME)

        monkeypatch.setattr("gardenlinux.s3.s3_artifacts.file_digest", dummy_digest)

        cname = make_cname()
        yield S3Env(s3, BUCKET_NAME, tmp_path, cname)
