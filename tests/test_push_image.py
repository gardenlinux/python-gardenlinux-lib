import json
import os
import tempfile

import pytest

from python_gardenlinux_lib.features import parse_features
from python_gardenlinux_lib.oci.registry import GlociRegistry
from python_gardenlinux_lib.cname import get_flavor_from_cname

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
def test_push_example(version, cname, arch):
    oci_metadata = parse_features.get_oci_metadata(
        cname, version, arch, GARDENLINUX_ROOT_DIR_EXAMPLE
    )
    container_name = f"{CONTAINER_NAME_ZOT_EXAMPLE}:{version}"
    a_registry = GlociRegistry(container_name=container_name, insecure=True)
    features = parse_features.get_features(cname, GARDENLINUX_ROOT_DIR_EXAMPLE)
    flavor = get_flavor_from_cname(cname, True)
    manifest_file = "/dev/null"

    commit = "test1234"

    a_registry.push_image_manifest(
        arch,
        cname,
        version,
        f"{GARDENLINUX_ROOT_DIR_EXAMPLE}/.build",
        oci_metadata,
        features,
        flavor,
        commit,
        manifest_file,
    )
