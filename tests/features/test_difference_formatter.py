import pathlib

import pytest

from gardenlinux.features.difference_formatter import Formatter

FLAVORS_MATRIX = {
    "include": [
        {"arch": "amd64", "flavor": "ali-gardener_prod"},
        {"arch": "amd64", "flavor": "aws-gardener_prod"},
        {"arch": "amd64", "flavor": "aws-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "aws-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "aws-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "azure-gardener_prod"},
        {"arch": "amd64", "flavor": "azure-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "azure-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "azure-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "container"},
        {"arch": "amd64", "flavor": "gcp-gardener_prod"},
        {"arch": "amd64", "flavor": "gcp-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "gcp-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "gcp-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "gdch-gardener_prod"},
        {"arch": "amd64", "flavor": "kvm-gardener_prod"},
        {"arch": "amd64", "flavor": "kvm-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "kvm-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "kvm-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "metal-capi"},
        {"arch": "amd64", "flavor": "metal-gardener_prod"},
        {"arch": "amd64", "flavor": "metal-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "metal-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "metal-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "metal-gardener_pxe"},
        {"arch": "amd64", "flavor": "metal-vhost"},
        {"arch": "amd64", "flavor": "metal_pxe"},
        {"arch": "amd64", "flavor": "openstack-gardener_prod"},
        {"arch": "amd64", "flavor": "openstack-gardener_prod_tpm2_trustedboot"},
        {"arch": "amd64", "flavor": "openstack-gardener_prod_trustedboot"},
        {"arch": "amd64", "flavor": "openstack-gardener_prod_usi"},
        {"arch": "amd64", "flavor": "openstackbaremetal-gardener_prod"},
        {"arch": "amd64", "flavor": "vmware-gardener_prod"},
        {"arch": "arm64", "flavor": "aws-gardener_prod"},
        {"arch": "arm64", "flavor": "aws-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "aws-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "aws-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "azure-gardener_prod"},
        {"arch": "arm64", "flavor": "azure-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "azure-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "azure-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "container"},
        {"arch": "arm64", "flavor": "gcp-gardener_prod"},
        {"arch": "arm64", "flavor": "gcp-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "gcp-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "gcp-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "gdch-gardener_prod"},
        {"arch": "arm64", "flavor": "kvm-gardener_prod"},
        {"arch": "arm64", "flavor": "kvm-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "kvm-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "kvm-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "metal-capi"},
        {"arch": "arm64", "flavor": "metal-gardener_prod"},
        {"arch": "arm64", "flavor": "metal-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "metal-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "metal-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "metal-gardener_pxe"},
        {"arch": "arm64", "flavor": "metal-vhost"},
        {"arch": "arm64", "flavor": "metal_pxe"},
        {"arch": "arm64", "flavor": "openstack-gardener_prod"},
        {"arch": "arm64", "flavor": "openstack-gardener_prod_tpm2_trustedboot"},
        {"arch": "arm64", "flavor": "openstack-gardener_prod_trustedboot"},
        {"arch": "arm64", "flavor": "openstack-gardener_prod_usi"},
        {"arch": "arm64", "flavor": "openstackbaremetal-gardener_prod"},
        {"arch": "arm64", "flavor": "vmware-gardener_prod"},
    ]
}
BARE_FLAVORS_MATRIX = {
    "include": [
        {"arch": "amd64", "flavor": "bare-libc"},
        {"arch": "amd64", "flavor": "bare-nodejs"},
        {"arch": "amd64", "flavor": "bare-python"},
        {"arch": "amd64", "flavor": "bare-sapmachine"},
        {"arch": "arm64", "flavor": "bare-libc"},
        {"arch": "arm64", "flavor": "bare-nodejs"},
        {"arch": "arm64", "flavor": "bare-python"},
        {"arch": "arm64", "flavor": "bare-sapmachine"},
    ]
}

gardenlinux_root = "test-data/gardenlinux"
diff_files = pathlib.Path("test-data/diff_files").resolve()


@pytest.mark.parametrize("i", [i.name for i in diff_files.iterdir() if i.is_dir()])
def test_formatter(i: str) -> None:
    nightly_stats = diff_files.joinpath(f"{i}-nightly_stats")

    if nightly_stats.is_file():
        formatter = Formatter(
            FLAVORS_MATRIX,
            BARE_FLAVORS_MATRIX,
            diff_files.joinpath(i),
            gardenlinux_root=gardenlinux_root,
            nightly_stats=nightly_stats,
        )
    else:
        formatter = Formatter(
            FLAVORS_MATRIX,
            BARE_FLAVORS_MATRIX,
            diff_files.joinpath(i),
            gardenlinux_root=gardenlinux_root,
        )

    with open(diff_files.joinpath(f"{i}.md"), "r") as f:
        expected = f.read()

    assert str(formatter) == expected
