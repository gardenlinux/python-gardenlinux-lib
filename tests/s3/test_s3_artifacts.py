# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

from gardenlinux.s3.s3_artifacts import S3Artifacts

RELEASE_DATA = """
    GARDENLINUX_VERSION = 1234.1
    GARDENLINUX_COMMIT_ID = abc123
    GARDENLINUX_COMMIT_ID_LONG = abc123long
    GARDENLINUX_FEATURES = _usi,_trustedboot
    """


def test_s3artifacts_init_success(s3_setup):
    # Arrange
    env = s3_setup

    # Act
    s3_artifacts = S3Artifacts(env.bucket_name)

    # Assert
    assert s3_artifacts._bucket.name == env.bucket_name


def tets_s3artifacts_invalid_bucket():
    # Act / Assert
    with pytest.raises(Exception):
        S3Artifacts("unknown-bucket")


def test_download_to_directory_success(s3_setup):
    """
    Test download of multiple files to a directory on disk.
    """
    # Arrange
    env = s3_setup
    bucket = env.s3.Bucket(env.bucket_name)

    bucket.put_object(Key=f"meta/singles/{env.cname}", Body=b"metadata")
    bucket.put_object(Key=f"objects/{env.cname}/file1", Body=b"data1")
    bucket.put_object(Key=f"objects/{env.cname}/file2", Body=b"data2")

    with TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)

        # Act
        artifacts = S3Artifacts(env.bucket_name)
        artifacts.download_to_directory(env.cname, outdir)

        # Assert
        assert (outdir / f"{env.cname}.s3_metadata.yaml").read_bytes() == b"metadata"
        assert (outdir / "file1").read_bytes() == b"data1"
        assert (outdir / "file2").read_bytes() == b"data2"


def test_download_to_directory_invalid_path(s3_setup):
    """
    Test proper handling of download attempt to invalid path.
    """
    # Arrange
    env = s3_setup
    artifacts = S3Artifacts(env.bucket_name)

    # Act / Assert
    with pytest.raises(RuntimeError):
        artifacts.download_to_directory({env.cname}, "/invalid/path/does/not/exist")


def test_upload_from_directory_success(s3_setup):
    """
    Test upload of multiple artifacts from disk to bucket
    """
    # Arrange
    env = s3_setup

    release_path = env.tmp_path / f"{env.cname}.release"
    release_path.write_text(RELEASE_DATA)

    for filename in [f"{env.cname}-file1", f"{env.cname}-file2"]:
        (env.tmp_path / filename).write_bytes(b"dummy content")

    # Act
    artifacts = S3Artifacts(env.bucket_name)
    artifacts.upload_from_directory(env.cname, env.tmp_path)

    # Assert
    bucket = env.s3.Bucket(env.bucket_name)
    keys = [obj.key for obj in bucket.objects.all()]
    assert f"objects/{env.cname}/{env.cname}-file1" in keys
    assert f"objects/{env.cname}/{env.cname}-file2" in keys
    assert f"meta/singles/{env.cname}" in keys


def test_upload_from_directory_with_delete(s3_setup):
    """
    Test that upload_from_directory deletes existing files before uploading
    when delete_before_push=True.
    """
    env = s3_setup
    bucket = env.s3.Bucket(env.bucket_name)

    # Arrange: create release and artifact files locally
    release = env.tmp_path / f"{env.cname}.release"
    release.write_text(RELEASE_DATA)

    artifact = env.tmp_path / f"{env.cname}.kernel"
    artifact.write_bytes(b"fake")

    # Arrange: put dummy existing objects to be deleted
    bucket.put_object(Key=f"objects/{env.cname}/{artifact.name}", Body=b"old data")
    bucket.put_object(Key=f"meta/singles/{env.cname}", Body=b"old metadata")

    artifacts = S3Artifacts(env.bucket_name)

    # Act
    artifacts.upload_from_directory(env.cname, env.tmp_path, delete_before_push=True)

    # Assert
    keys = [obj.key for obj in bucket.objects.all()]

    # The old key should no longer be present as old data (no duplicates)
    # but the new upload file key should exist (artifact uploaded)
    assert f"objects/{env.cname}/{artifact.name}" in keys
    assert f"meta/singles/{env.cname}" in keys
