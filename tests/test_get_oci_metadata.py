import pytest

from python_gardenlinux_lib.features.parse_features import get_oci_metadata
from tests.conftest import GL_ROOT_DIR


@pytest.mark.parametrize(
    "input_cname, version, arch",
    [
        #("aws-gardener_prod", "today"),
        #("openstack-gardener_prod", "today"),
        ("openstack-gardener_pxe", "1443.9", "amd64"),
    ],
)
def test_get_oci_metadata(input_cname: str, version: str, arch: str):
    """
    Work in Progess: currently only used to see what get_oci_metadata returns
    """
    metadata = get_oci_metadata(input_cname, version, arch, GL_ROOT_DIR)
    print()
    for elem in metadata:
        print(elem["file_name"], "\tmedia-type:",   elem["media_type"], "\t annotations", elem["annotations"])