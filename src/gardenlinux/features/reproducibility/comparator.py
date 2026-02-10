# -*- coding: utf-8 -*-

"""
diff-files comparator generating the list of files for reproducibility test workflow
"""

import filecmp
import json
import re
import tarfile
import tempfile
from os import PathLike
from pathlib import Path
from typing import Optional


class Comparator(object):
    """
    This class takes either two .tar or two .oci files and identifies differences in the filesystems

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    _default_whitelist: list[str] = []

    _nightly_whitelist = [
        r"/etc/apt/sources\.list\.d/gardenlinux\.sources",
        r"/etc/os-release",
        r"/etc/shadow",
        r"/etc/update-motd\.d/05-logo",
        r"/var/lib/apt/lists/packages\.gardenlinux\.io_gardenlinux_dists_[0-9]*\.[0-9]*\.[0-9]*_.*",
        r"/var/lib/apt/lists/packages\.gardenlinux\.io_gardenlinux_dists_[0-9]*\.[0-9]*\.[0-9]*_main_binary-(arm64|amd64)_Packages",
        r"/efi/loader/entries/Default-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)\.conf",
        r"/efi/Default/[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)/initrd",
        r"/boot/initrd\.img-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)",
    ]

    def __init__(
        self, nightly: bool = False, whitelist: list[str] = _default_whitelist
    ):
        """
        Constructor __init__(Comparator)

        :param nightly:                 Flag indicating if the nightlywhitelist should be used
        :param whitelst:                Additional whitelist

        :since: 1.0.0
        """
        self.whitelist = whitelist
        if nightly:
            self.whitelist += self._nightly_whitelist

    @staticmethod
    def _unpack(file: PathLike[str]) -> tempfile.TemporaryDirectory[str]:
        """
        Unpack a .tar archive or .oci image into a temporary dictionary

        :param file:                    .tar or .oci file

        :return: TemporaryDirectory     Temporary directory containing the unpacked file
        :since: 1.0.0
        """

        output_dir = tempfile.TemporaryDirectory()
        file = Path(file).resolve()
        if file.name.endswith(".oci"):
            with tempfile.TemporaryDirectory() as extracted:
                # Extract .oci file
                with tarfile.open(file, "r") as tar:
                    tar.extractall(path=extracted)

                layers_dir = Path(extracted).joinpath("blobs/sha256")
                assert layers_dir.is_dir()

                with open(Path(extracted).joinpath("index.json"), "r") as f:
                    index = json.load(f)

                # Only support first manifest
                manifest = index["manifests"][0]["digest"].split(":")[1]

                with open(layers_dir.joinpath(manifest), "r") as f:
                    manifest = json.load(f)

                layers = [layer["digest"].split(":")[1] for layer in manifest["layers"]]

                # Extract layers in order
                for layer in layers:
                    layer_path = layers_dir.joinpath(layer)
                    if tarfile.is_tarfile(layer_path):
                        with tarfile.open(layer_path, "r") as tar:
                            for member in tar.getmembers():
                                try:
                                    tar.extract(member, path=output_dir.name)
                                except tarfile.AbsoluteLinkError:
                                    # Convert absolute link to relative link
                                    member.linkpath = (
                                        "../" * member.path.count("/")
                                        + member.linkpath[1:]
                                    )
                                    tar.extract(member, path=output_dir.name)
                                except tarfile.TarError as e:
                                    print(f"Skipping {member.name} due to error: {e}")
        else:
            with tarfile.open(file, "r") as tar:
                tar.extractall(path=output_dir.name, filter="fully_trusted")

        return output_dir

    def _diff_files(
        self, cmp: filecmp.dircmp[str], left_root: Optional[Path] = None
    ) -> list[str]:
        """
        Recursively compare files

        :param cmp:                     Dircmp to recursively compare
        :param left_root:               Left root to obtain the archive relative path

        :return: list[Path]             List of paths with different content
        :since: 1.0.0
        """

        result = []
        if not left_root:
            left_root = Path(cmp.left)
        for name in cmp.diff_files:
            result.append(f"/{Path(cmp.left).relative_to(left_root).joinpath(name)}")
        for sub_cmp in cmp.subdirs.values():
            result += self._diff_files(sub_cmp, left_root=left_root)
        return result

    def generate(self, a: PathLike[str], b: PathLike[str]) -> tuple[list[str], bool]:
        """
        Compare two .tar/.oci images with each other

        :param a:                       First .tar/.oci file
        :param b:                       Second .tar/.oci file

        :return: list[Path], bool       Filtered list of paths with different content and flag indicating if whitelist was applied
        :since: 1.0.0
        """

        if filecmp.cmp(a, b, shallow=False):
            return [], False

        with self._unpack(a) as unpacked_a, self._unpack(b) as unpacked_b:
            cmp = filecmp.dircmp(unpacked_a, unpacked_b, shallow=False)

            diff_files = self._diff_files(cmp)

        filtered = [
            file
            for file in diff_files
            if not any(re.match(pattern, file) for pattern in self.whitelist)
        ]
        whitelist = len(diff_files) != len(filtered)

        return filtered, whitelist
