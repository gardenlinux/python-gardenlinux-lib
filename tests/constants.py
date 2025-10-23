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
TEST_GARDENLINUX_COMMIT_SHORT = TEST_GARDENLINUX_COMMIT[:8]
TEST_GARDENLINUX_RELEASE_BUCKET_NAME = "test__gardenlinux__releases"

RELEASE_NOTES_TEST_DATA_DIR = (
    Path(os.path.dirname(__file__)) / ".." / "test-data" / "release_notes"
)
RELEASE_NOTES_S3_ARTIFACTS_DIR = RELEASE_NOTES_TEST_DATA_DIR / "s3_bucket_artifacts"

RELEASE_ARTIFACTS_METADATA_FILES = [
    "ali-gardener_prod-amd64.s3_metadata.yaml",
    "aws-gardener_prod-amd64.s3_metadata.yaml",
    "aws-gardener_prod-arm64.s3_metadata.yaml",
    "aws-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "aws-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "aws-gardener_prod_usi-amd64.s3_metadata.yaml",
    "aws-gardener_prod_usi-arm64.s3_metadata.yaml",
    "azure-gardener_prod-amd64.s3_metadata.yaml",
    "azure-gardener_prod-arm64.s3_metadata.yaml",
    "azure-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "azure-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "azure-gardener_prod_usi-amd64.s3_metadata.yaml",
    "azure-gardener_prod_usi-arm64.s3_metadata.yaml",
    "container-amd64.s3_metadata.yaml",
    "container-arm64.s3_metadata.yaml",
    "gcp-gardener_prod-amd64.s3_metadata.yaml",
    "gcp-gardener_prod-arm64.s3_metadata.yaml",
    "gcp-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "gcp-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "gcp-gardener_prod_usi-amd64.s3_metadata.yaml",
    "gcp-gardener_prod_usi-arm64.s3_metadata.yaml",
    "gdch-gardener_prod-amd64.s3_metadata.yaml",
    "gdch-gardener_prod-arm64.s3_metadata.yaml",
    "kvm-gardener_prod-amd64.s3_metadata.yaml",
    "kvm-gardener_prod-arm64.s3_metadata.yaml",
    "kvm-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "kvm-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "kvm-gardener_prod_usi-amd64.s3_metadata.yaml",
    "kvm-gardener_prod_usi-arm64.s3_metadata.yaml",
    "metal-capi-amd64.s3_metadata.yaml",
    "metal-capi-arm64.s3_metadata.yaml",
    "metal-gardener_prod-amd64.s3_metadata.yaml",
    "metal-gardener_prod-arm64.s3_metadata.yaml",
    "metal-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "metal-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "metal-gardener_prod_usi-amd64.s3_metadata.yaml",
    "metal-gardener_prod_usi-arm64.s3_metadata.yaml",
    "metal-gardener_pxe-amd64.s3_metadata.yaml",
    "metal-gardener_pxe-arm64.s3_metadata.yaml",
    "metal_pxe-amd64.s3_metadata.yaml",
    "metal_pxe-arm64.s3_metadata.yaml",
    "metal-vhost-amd64.s3_metadata.yaml",
    "metal-vhost-arm64.s3_metadata.yaml",
    "openstackbaremetal-gardener_prod-amd64.s3_metadata.yaml",
    "openstackbaremetal-gardener_prod-arm64.s3_metadata.yaml",
    "openstack-gardener_prod-amd64.s3_metadata.yaml",
    "openstack-gardener_prod-arm64.s3_metadata.yaml",
    "openstack-gardener_prod_tpm2_trustedboot-amd64.s3_metadata.yaml",
    "openstack-gardener_prod_tpm2_trustedboot-arm64.s3_metadata.yaml",
    "openstack-gardener_prod_usi-amd64.s3_metadata.yaml",
    "openstack-gardener_prod_usi-arm64.s3_metadata.yaml",
    "vmware-gardener_prod-amd64.s3_metadata.yaml",
    "vmware-gardener_prod-arm64.s3_metadata.yaml",
]
