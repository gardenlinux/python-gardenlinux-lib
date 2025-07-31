import pytest
from pathlib import Path
from moto import mock_aws
from hashlib import md5, sha256
import boto3


# Dummy CName replacement
class DummyCName:
    def __init__(self, cname):  # pylint: disable=unused-argument
        self.platform = "aws"
        self.arch = "amd64"
        self.version = "1234.1"
        self.commit_id = "abc123"


# Helpers to compute digests for fake files
def dummy_digest(data: bytes, algo: str) -> str:
    """
    Dummy for file_digest() to compute hashes for in-memory byte streams
    """
    content = data.read()
    data.seek(0)  # Reset byte cursor to start for multiple uses

    if algo == "md5":
        return md5(content)  # nosec B324
    elif algo == "sha256":
        return sha256(content)
    else:
        raise ValueError(f"Unsupported algo: {algo}")


@pytest.fixture(autouse=True)
def s3_setup(tmp_path, monkeypatch):
    """
    Provides a clean S3 setup for each test.
    """
    with mock_aws():
        s3 = boto3.resource("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3.create_bucket(Bucket=bucket_name)

        monkeypatch.setattr("gardenlinux.s3.s3_artifacts.CName", DummyCName)
        monkeypatch.setattr("gardenlinux.s3.s3_artifacts.file_digest", dummy_digest)

        yield s3, bucket_name, tmp_path
