import pytest

from python_gardenlinux_lib.parse_features import get_oci_metadata
from tests.conftest import GL_ROOT_DIR


@pytest.mark.parametrize(
    "input_cname, version",
    [
        ("aws-gardener_prod", "today"),
        ("openstack-gardener_prod", "today"),
    ],
)
def test_get_features_dict(input_cname: str, version: str):
    """
    Work in Progess: currently only used to see what get_oci_metadata returns
    """
    metadata = get_oci_metadata(input_cname, version, GL_ROOT_DIR)
    print(metadata)
