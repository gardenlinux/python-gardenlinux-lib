import pytest

from python_gardenlinux_lib.features.parse_features import get_oci_metadata
from .constants import GL_ROOT_DIR


@pytest.mark.parametrize(
    "input_cname, version, arch",
    [
        # ("aws-gardener_prod", "today"),
        # ("openstack-gardener_prod", "today"),
        ("openstack-gardener_pxe", "1443.9", "amd64"),
    ],
)
def test_get_oci_metadata(input_cname: str, version: str, arch: str):
    """
    Work in Progess: currently only used to see what get_oci_metadata returns
    """
    metadata = get_oci_metadata(input_cname, version, arch, GL_ROOT_DIR)
    expected = [
        {
            "file_name": "openstack-gardener_pxe-amd64-1443.9-c81fcc9f.qcow2",
            "media_type": "application/io.gardenlinux.image.format.qcow2",
            "annotations": {"io.gardenlinux.image.layer.architecture": "amd64"},
        },
        {
            "file_name": "openstack-gardener_pxe-amd64-1443.9-c81fcc9f.vmdk",
            "media_type": "application/io.gardenlinux.image.format.vmdk",
            "annotations": {"io.gardenlinux.image.layer.architecture": "amd64"},
        },
        {
            "file_name": "openstack-gardener_pxe-amd64-1443.9-c81fcc9f.tar",
            "media_type": "application/io.gardenlinux.image.archive.format.tar",
            "annotations": {"io.gardenlinux.image.layer.architecture": "amd64"},
        },
    ]
    for elem in metadata:
        print(
            elem["file_name"],
            "\tmedia-type:",
            elem["media_type"],
            "\t annotations",
            elem["annotations"],
            "\tkeys:",
            elem.keys(),
        )
    # assert metadata == expected
