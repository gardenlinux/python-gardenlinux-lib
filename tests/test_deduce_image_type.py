from python_gardenlinux_lib.features.parse_features import (
    deduce_archive_filetypes,
    deduce_image_filetypes,
)
import pytest

from .constants import GL_ROOT_DIR


@pytest.mark.parametrize(
    "feature_name, expected_file_type",
    [
        ("ali", ["qcow2"]),
        ("azure", ["vhd"]),
        ("gcp", ["gcpimage.tar.gz"]),
        ("gdch", ["gcpimage.tar.gz"]),
        ("openstack", ["qcow2", "vmdk"]),
        ("openstackbaremetal", ["qcow2", "vmdk"]),
        ("vmware", ["ova"]),
    ],
)
def test_deduce_image_type(feature_name, expected_file_type):
    file_type = deduce_image_filetypes(f"{GL_ROOT_DIR}/features/{feature_name}")
    assert sorted(expected_file_type) == file_type


@pytest.mark.parametrize(
    "feature_name, expected_file_type",
    [
        ("_bfpxe", ["pxe.tar.gz"]),
        ("_iso", ["iso"]),
        ("_pxe", ["pxe.tar.gz"]),
        ("container", ["oci"]),
        ("firecracker", ["firecracker.tar.gz"]),
    ],
)
def test_deduce_archive_type(feature_name, expected_file_type):
    file_type = deduce_archive_filetypes(f"{GL_ROOT_DIR}/features/{feature_name}")
    assert sorted(expected_file_type) == file_type
