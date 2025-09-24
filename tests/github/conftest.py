import os
import shutil
from pathlib import Path

import pytest

from ..constants import RELEASE_ID_FILE, S3_DOWNLOADS_DIR


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
