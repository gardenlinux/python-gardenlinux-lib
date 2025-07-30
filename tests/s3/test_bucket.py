"""
Test the `Bucket` class in `src/gardenlinux/s3/bucket.py` by using
mock AWS interactions provided by the `moto` module.

The `@mock_aws` decorator `moto` provides ensures a fresh
but fake AWS-like environment.
"""

import io
import pytest
import boto3
from moto import mock_aws
from pathlib import Path

from gardenlinux.s3.bucket import Bucket


BUCKET_NAME = "test-bucket"
REGION = "us-east-1"


@mock_aws
def test_objects_empty():
    """
    List objects from empty bucket.
    """
    # Arrange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)

    # Act
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})
    objects = list(bucket.objects)

    # Assert
    assert objects == []


@mock_aws
def test_upload_file_and_list(tmp_path):
    """
    Create a fake file in a temporary directory, upload and try
    to list it
    """
    # Arrange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)

    test_file = tmp_path / "example.txt"
    test_file.write_text("hello moto")

    # Act
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})
    bucket.upload_file(str(test_file), "example.txt")

    all_keys = [obj.key for obj in bucket.objects]

    # Assert
    assert "example.txt" in all_keys


@mock_aws
def test_download_file(tmp_path):
    """
    Try to download a file pre-existing in the bucket
    """
    # Arrange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)
    s3.Object(BUCKET_NAME, "file.txt").put(Body=b"some data")

    # Act
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})

    target_path = tmp_path / "downloaded.txt"
    bucket.download_file("file.txt", str(target_path))

    # Assert
    assert target_path.read_text() == "some data"


@mock_aws
def test_upload_fileobj():
    """
    Upload a file-like in-memory object to the bucket
    """
    # Arrange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)

    # Act
    # Create in-memory binary stream (file content)
    data = io.BytesIO(b"Test Data")
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})
    bucket.upload_fileobj(data, "binary.obj")

    obj = s3.Object(BUCKET_NAME, "binary.obj").get()

    # Assert
    assert obj["Body"].read() == b"Test Data"


@mock_aws
def test_download_fileobj():
    """
    Download data into a in-memory object
    """
    # Arange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)
    # Put some object in the bucket
    s3.Object(BUCKET_NAME, "somekey").put(Body=b"123abc")

    # Act
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})

    # Create empty in-memory bytestream to act as a writable file
    output = io.BytesIO()
    bucket.download_fileobj("somekey", output)

    # Reset binary cursor to prepare for read
    output.seek(0)

    # Assert
    assert output.read() == b"123abc"


@mock_aws
def test_getattr_delegates():
    """
    Verify that attribute access is delegated to the underlying boto3 Bucket.

    This checks that accessing e.g. `.name` on our custom Bucket works by forwarding
    the call to the real boto3 bucket.
    """
    # Arrange
    s3 = boto3.resource("s3", region_name=REGION)
    s3.create_bucket(Bucket=BUCKET_NAME)

    # Act
    bucket = Bucket(bucket_name=BUCKET_NAME, s3_resource_config={"region_name": REGION})

    # Assert
    # __getattr__ should delegate this to the underlying boto3 Bucket object
    assert bucket.name == BUCKET_NAME
