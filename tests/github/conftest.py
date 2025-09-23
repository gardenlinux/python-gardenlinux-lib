import os
import shutil

import pytest

from ..constants import S3_DOWNLOADS_DIR


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
