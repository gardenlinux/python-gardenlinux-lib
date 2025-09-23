# -*- coding: utf-8 -*-

import os
from pathlib import Path

from gardenlinux.git import Repository

TEST_DATA_DIR = "test-data"
GL_ROOT_DIR = f"{TEST_DATA_DIR}/gardenlinux"
CERT_DIR = f"{TEST_DATA_DIR}/cert"

ZOT_CONFIG_FILE = f"{TEST_DATA_DIR}/zot/config.json"
REGISTRY = "127.0.0.1:18081"
REGISTRY_URL = f"http://{REGISTRY}"
REPO_NAME = "gardenlinux-example"
CONTAINER_NAME_ZOT_EXAMPLE = f"{REGISTRY}/{REPO_NAME}"
GARDENLINUX_ROOT_DIR_EXAMPLE = f"{TEST_DATA_DIR}/gardenlinux/.build"

TEST_PLATFORMS = ["aws", "azure", "gcp", "openstack", "openstackbaremetal", "metal"]
TEST_ARCHITECTURES = ["arm64", "amd64"]
TEST_FEATURE_STRINGS_SHORT = ["gardener_prod"]
TEST_FEATURE_SET = "_slim,base,container"
TEST_COMMIT = Repository(GL_ROOT_DIR).commit_id[:8]
TEST_VERSION = "1000.0"
TEST_VERSION_STABLE = "1000"

TEST_GARDENLINUX_RELEASE = "1877.3"
TEST_GARDENLINUX_COMMIT = "75df9f401a842914563f312899ec3ce34b24515c"

S3_DOWNLOADS_DIR = Path(os.path.dirname(__file__)) / ".." / "s3_downloads"
