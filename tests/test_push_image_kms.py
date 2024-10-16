import pytest

from python_gardenlinux_lib.features import parse_features
from python_gardenlinux_lib.oras.crypto import KMSSigner
from python_gardenlinux_lib.oras.registry import GlociRegistry

CONTAINER_NAME_ZOT_EXAMPLE = "127.0.0.1:18081/gardenlinux-example"
GARDENLINUX_ROOT_DIR_EXAMPLE = "test-data/gardenlinux/"


@pytest.mark.usefixtures("zot_session")
@pytest.mark.parametrize(
    "version, cname, arch",
    [
        ("today", "aws-gardener_prod", "arm64"),
        ("today", "aws-gardener_prod", "amd64"),
        ("today", "gcp-gardener_prod", "arm64"),
        ("today", "gcp-gardener_prod", "amd64"),
        ("today", "azure-gardener_prod", "arm64"),
        ("today", "azure-gardener_prod", "amd64"),
        ("today", "openstack-gardener_prod", "arm64"),
        ("today", "openstack-gardener_prod", "amd64"),
        ("today", "openstackbaremetal-gardener_prod", "arm64"),
        ("today", "openstackbaremetal-gardener_prod", "amd64"),
        ("today", "metal-kvm_dev", "arm64"),
        ("today", "metal-kvm_dev", "amd64"),
    ],
)
def test_push_example_kms(version, cname, arch):
    oci_metadata = parse_features.get_oci_metadata(
        cname, version, arch, GARDENLINUX_ROOT_DIR_EXAMPLE
    )
    container_name = f"{CONTAINER_NAME_ZOT_EXAMPLE}:{version}"
    signer = KMSSigner(arn="b70b0b19-389a-4b3d-b82a-77279a98ed23")
    registry = GlociRegistry(
        container_name=container_name, insecure=True, signer=signer
    )
    features = parse_features.get_features(cname, GARDENLINUX_ROOT_DIR_EXAMPLE)
    registry.push_image_manifest(
        arch,
        cname,
        version,
        f"{GARDENLINUX_ROOT_DIR_EXAMPLE}/.build",
        oci_metadata,
        features,
    )
