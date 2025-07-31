# -*- coding: utf-8 -*-

"""
Test the `Bucket` class in `src/gardenlinux/s3/bucket.py` by using
mock AWS interactions provided by the `moto` module.

A mock AWS environment is provided by the `s3_setup` fixture found in `conftest.py`.
"""

from pathlib import Path
import io
import pytest

from gardenlinux.s3.bucket import Bucket


REGION = "us-east-1"


def test_objects_empty(s3_setup):
    """
    List objects from empty bucket.
    """
    # Arrange
    env = s3_setup

    # Act
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})

    # Assert
    assert list(bucket.objects) == []


def test_upload_file_and_list(s3_setup):
    """
    Create a fake file in a temporary directory, upload and try
    to list it
    """
    # Arrange
    env = s3_setup

    test_file = env.tmp_path / "example.txt"
    test_file.write_text("hello moto")

    # Act
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})
    bucket.upload_file(str(test_file), "example.txt")

    all_keys = [obj.key for obj in bucket.objects]

    # Assert
    assert "example.txt" in all_keys


def test_download_file(s3_setup):
    """
    Try to download a file pre-existing in the bucket
    """
    # Arrange
    env = s3_setup
    env.s3.Object(env.bucket_name, "file.txt").put(Body=b"some data")

    # Act
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})
    target_path = env.tmp_path / "downloaded.txt"
    bucket.download_file("file.txt", str(target_path))

    # Assert
    assert target_path.read_text() == "some data"


def test_upload_fileobj(s3_setup):
    """
    Upload a file-like in-memory object to the bucket
    """
    # Arrange
    env = s3_setup

    # Act
    # Create in-memory binary stream (file content)
    data = io.BytesIO(b"Test Data")
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})
    bucket.upload_fileobj(data, "binary.obj")

    obj = env.s3.Object(env.bucket_name, "binary.obj").get()

    # Assert
    assert obj["Body"].read() == b"Test Data"


def test_download_fileobj(s3_setup):
    """
    Download data into a in-memory object
    """
    # Arange
    env = s3_setup
    # Put some object in the bucket
    env.s3.Object(env.bucket_name, "somekey").put(Body=b"123abc")

    # Act
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})
    # Create empty in-memory bytestream to act as a writable file
    output = io.BytesIO()
    bucket.download_fileobj("somekey", output)
    # Reset binary cursor to prepare for read
    output.seek(0)

    # Assert
    assert output.read() == b"123abc"


def test_getattr_delegates(s3_setup):
    """
    Verify that attribute access is delegated to the underlying boto3 Bucket.

    This checks that accessing e.g. `.name` on our custom Bucket works by forwarding
    the call to the real boto3 bucket.
    """
    # Arrange
    env = s3_setup

    # Act
    bucket = Bucket(env.bucket_name, s3_resource_config={"region_name": REGION})

    # Assert
    # __getattr__ should delegate this to the underlying boto3 Bucket object
    assert bucket.name == env.bucket_name
