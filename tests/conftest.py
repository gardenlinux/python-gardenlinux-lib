from git import Repo
import os
import shutil
import pytest


GL_ROOT_DIR = "gardenlinux"
GL_REPO_URL = "https://github.com/gardenlinux/gardenlinux"

@pytest.fixture(autouse=True, scope="session")
def setup_repo():
    """
    Clone gardenlinux repo to local path for tests
    and cleanup after test session.
    """
    Repo.clone_from(GL_REPO_URL, GL_ROOT_DIR)
    print(GL_ROOT_DIR)
    yield
    if os.path.isdir(GL_ROOT_DIR):
        shutil.rmtree(GL_ROOT_DIR)
