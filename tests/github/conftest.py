import os
import shutil
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from gardenlinux.constants import RELEASE_ID_FILE, S3_DOWNLOADS_DIR

from ..constants import TEST_GARDENLINUX_RELEASE_BUCKET_NAME


@pytest.fixture
def downloads_dir():
    os.makedirs(S3_DOWNLOADS_DIR, exist_ok=True)
    yield
    shutil.rmtree(S3_DOWNLOADS_DIR)


@pytest.fixture
def github_token():
    os.environ["GITHUB_TOKEN"] = "foobarbazquux"
    yield
    del os.environ["GITHUB_TOKEN"]


@pytest.fixture
def artifact_for_upload(downloads_dir):
    artifact = S3_DOWNLOADS_DIR / "artifact.log"
    artifact.touch()
    yield artifact
    artifact.unlink()


@pytest.fixture
def release_id_file():
    f = Path(RELEASE_ID_FILE)
    yield f
    f.unlink()


@pytest.fixture
def release_s3_bucket():
    with mock_aws():
        s3 = boto3.resource("s3", region_name="eu-central-1")
        s3.create_bucket(
            Bucket=TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
        )
        yield s3.Bucket(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)


@pytest.fixture
def blackhole_s3_bucket():
    """This fixture yields an object that behaves as an S3 bucket where
    any object can be found, but downloading a file always raises an exception.
    This is needed to test the retry mechanism as the object also counts
    how many times an exception was raised."""

    class BlackHoleObject:
        def __init__(self, bucket_name, key):
            self.bucket_name = bucket_name
            self.key = key

    class BlackHoleObjects:
        def __init__(self, bucket_name):
            self.bucket_name = bucket_name

        def filter(self, Prefix):
            return [BlackHoleObject(self.bucket_name, Prefix)]

    class BlackHoleS3Bucket:
        def __init__(self, bucket_name):
            self.objects = BlackHoleObjects(bucket_name)
            self.download_attempts = 0

        def download_file(self, x, y):
            self.download_attempts += 1
            raise IOError(f"Download attempt # {self.download_attempts} failed")

    yield BlackHoleS3Bucket(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)


@pytest.fixture
def metadata_file():
    pass
