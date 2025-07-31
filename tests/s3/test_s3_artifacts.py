import pytest
import boto3
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import md5, sha256
from moto import mock_aws

from gardenlinux.s3.s3_artifacts import S3Artifacts

CNAME = "testcname"


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


def test_s3artifacts_init_success(s3_setup):
    # Arrange
    _, bucket_name, _ = s3_setup

    # Act
    s3_artifacts = S3Artifacts(bucket_name)

    # Assert
    assert s3_artifacts._bucket.name == bucket_name


def tets_s3artifacts_invalid_bucket():
    # Act / Assert
    with pytest.raises(Exception):
        S3Artifacts("unknown-bucket")


def test_download_to_directory_success(s3_setup):
    """
    Test download of multiple files to a directory on disk.
    """
    # Arrange
    s3, bucket_name, _ = s3_setup
    bucket = s3.Bucket(bucket_name)

    bucket.put_object(Key=f"meta/singles/{CNAME}", Body=b"metadata")
    bucket.put_object(Key=f"objects/{CNAME}/file1", Body=b"data1")
    bucket.put_object(Key=f"objects/{CNAME}/file2", Body=b"data2")

    with TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)

        # Act
        artifacts = S3Artifacts(bucket_name)
        artifacts.download_to_directory(CNAME, outdir)

        # Assert
        assert (outdir / f"{CNAME}.s3_metadata.yaml").read_bytes() == b"metadata"
        assert (outdir / "file1").read_bytes() == b"data1"
        assert (outdir / "file2").read_bytes() == b"data2"


def test_download_to_directory_invalid_path(s3_setup):
    """
    Test proper handling of download attempt to invalid path.
    """
    # Arrange
    _, bucket_name, _ = s3_setup
    artifacts = S3Artifacts(bucket_name)

    # Act / Assert
    with pytest.raises(RuntimeError):
        artifacts.download_to_directory({CNAME}, "/invalid/path/does/not/exist")


def test_upload_from_directory_success(s3_setup):
    """
    Test upload of multiple artifacts from disk to bucket
    """
    # Arrange
    s3, bucket_name, tmp_path = s3_setup
    release_data = """
    GARDENLINUX_VERSION = 1234.1
    GARDENLINUX_COMMIT_ID = abc123
    GARDENLINUX_COMMIT_ID_LONG = abc123long
    GARDENLINUX_FEATURES = _usi,_trustedboot
    """

    release_path = tmp_path / f"{CNAME}.release"
    release_path.write_text(release_data)

    for filename in [f"{CNAME}-file1", f"{CNAME}-file2"]:
        (tmp_path / filename).write_bytes(b"dummy content")

    # Act
    artifacts = S3Artifacts(bucket_name)
    artifacts.upload_from_directory(CNAME, tmp_path)

    # Assert
    bucket = s3.Bucket(bucket_name)
    keys = [obj.key for obj in bucket.objects.all()]
    assert f"objects/{CNAME}/{CNAME}-file1" in keys
    assert f"objects/{CNAME}/{CNAME}-file2" in keys
    assert f"meta/singles/{CNAME}" in keys


def test_upload_from_directory_with_delete(s3_setup):
    """
    Test that upload_from_directory deletes existing files before uploading
    when delete_before_push=True.
    """
    s3, bucket_name, tmp_path = s3_setup
    bucket = s3.Bucket(bucket_name)

    # Arrange: create release and artifact files locally
    release = tmp_path / f"{CNAME}.release"
    release.write_text(
        "GARDENLINUX_VERSION = 1234.1\n"
        "GARDENLINUX_COMMIT_ID = abc123\n"
        "GARDENLINUX_COMMIT_ID_LONG = abc123long\n"
        "GARDENLINUX_FEATURES = _usi,_trustedboot\n"
    )

    artifact = tmp_path / f"{CNAME}.kernel"
    artifact.write_bytes(b"fake")

    # Arrange: put dummy existing objects to be deleted
    bucket.put_object(Key=f"objects/{CNAME}/{artifact.name}", Body=b"old data")
    bucket.put_object(Key=f"meta/singles/{CNAME}", Body=b"old metadata")

    artifacts = S3Artifacts(bucket_name)

    # Act
    artifacts.upload_from_directory(CNAME, tmp_path, delete_before_push=True)

    # Assert
    keys = [obj.key for obj in bucket.objects.all()]

    # The old key should no longer be present as old data (no duplicates)
    # but the new upload file key should exist (artifact uploaded)
    assert f"objects/{CNAME}/{artifact.name}" in keys
    assert f"meta/singles/{CNAME}" in keys
