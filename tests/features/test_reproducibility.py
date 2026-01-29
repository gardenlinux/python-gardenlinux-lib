import json
import sys
from pathlib import Path

import pytest

from gardenlinux.features.reproducibility.__main__ import main
from gardenlinux.features.reproducibility.comparator import Comparator
from gardenlinux.features.reproducibility.markdown_formatter import MarkdownFormatter

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

gardenlinux_root = Path("test-data/gardenlinux")
diff_files = Path("test-data/reproducibility/diff_files").resolve()
compare_files = Path("test-data/reproducibility/compare").resolve()


@pytest.mark.parametrize("i", [i.name for i in diff_files.iterdir() if i.is_dir()])
def test_formatter(i: str) -> None:
    nightly_stats = diff_files.joinpath(f"{i}-nightly_stats.csv")

    if nightly_stats.is_file():
        formatter = MarkdownFormatter(
            FLAVORS_MATRIX,
            BARE_FLAVORS_MATRIX,
            diff_files.joinpath(i),
            gardenlinux_root=str(gardenlinux_root),
            nightly_stats=nightly_stats,
        )
    else:
        formatter = MarkdownFormatter(
            FLAVORS_MATRIX,
            BARE_FLAVORS_MATRIX,
            diff_files.joinpath(i),
            gardenlinux_root=str(gardenlinux_root),
        )

    with open(diff_files.joinpath(f"{i}.md"), "r") as f:
        expected = f.read()

    assert str(formatter) == expected


@pytest.mark.parametrize("i", [i.name for i in diff_files.iterdir() if i.is_dir()])
def test_formatter_main(
    i: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    nightly_stats = diff_files.joinpath(f"{i}-nightly_stats.csv")

    argv = [
        "gl-diff",
        "format",
        "--feature-dir",
        str(gardenlinux_root.joinpath("features")),
        "--diff-dir",
        str(diff_files.joinpath(i)),
        json.dumps(FLAVORS_MATRIX),
        json.dumps(BARE_FLAVORS_MATRIX),
    ]

    if nightly_stats.is_file():
        argv = argv[:6] + ["--nightly-stats", str(nightly_stats)] + argv[6:]

    monkeypatch.setattr(sys, "argv", argv)

    main()

    received = capsys.readouterr().out

    with open(diff_files.joinpath(f"{i}.md"), "r") as f:
        expected = f.read()

    assert received == expected


def test_comparator() -> None:
    comparator = Comparator()

    files, whitelist = comparator.generate(
        compare_files.joinpath("a.tar"), compare_files.joinpath("b.tar")
    )

    assert not whitelist, "Whitelist is empty and should not filter anything"

    assert files == ["/a/b/c.txt"]


def test_comparator_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = [
        "gl-diff",
        "generate",
        str(compare_files.joinpath("a.tar")),
        str(compare_files.joinpath("b.tar")),
    ]

    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit) as pytest_exit:
        main()

    received = capsys.readouterr().out

    assert received == "/a/b/c.txt\n"
    assert pytest_exit.type == SystemExit
    assert pytest_exit.value.code == 1
