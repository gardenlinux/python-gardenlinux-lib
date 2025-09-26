import os
import shutil
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME, RELEASE_ID_FILE, S3_DOWNLOADS_DIR


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
        s3.create_bucket(Bucket=GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME,
                         CreateBucketConfiguration={
                             'LocationConstraint': 'eu-central-1'})
        yield s3.Bucket(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)


@pytest.fixture
def metadata_file():
    pass
