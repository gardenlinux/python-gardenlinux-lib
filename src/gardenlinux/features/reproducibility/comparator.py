# -*- coding: utf-8 -*-

"""
diff-files comparator generating the list of files for reproducibility test workflow
"""

import filecmp
import json
import logging
import re
import tarfile
import tempfile
from os import PathLike
from pathlib import Path
from typing import Any, Optional

import patoolib


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
        r"/var/lib/apt/lists/packages\.gardenlinux\.io_gardenlinux_dists_[0-9]*\.[0-9]*\.[0-9]*_main_binary-ARCH_Packages",
        r"/efi/loader/entries/Default-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?ARCH\.conf",
        r"/efi/Default/[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?ARCH/initrd",
        r"/boot/initrd\.img-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?ARCH",
    ]

    _cname = re.compile(
        r"[a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*-([0-9.]+|local)-([a-f0-9]{8}|today)"
    )

    _arch = re.compile(r"(arm64|amd64)")

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

        # Mute INFO logs from patool
        patool_logger = logging.getLogger("patool")
        patool_logger.setLevel("WARNING")

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
                    tar.extractall(
                        path=extracted, filter="fully_trusted", members=tar.getmembers()
                    )

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
                                    tar.extract(
                                        member,
                                        path=output_dir.name,
                                        filter="fully_trusted",
                                    )
                                except tarfile.AbsoluteLinkError:
                                    # Convert absolute link to relative link
                                    member.linkpath = (
                                        "../" * member.path.count("/")
                                        + member.linkpath[1:]
                                    )
                                    tar.extract(
                                        member,
                                        path=output_dir.name,
                                        filter="fully_trusted",
                                    )
                                except tarfile.TarError as e:
                                    print(f"Skipping {member.name} due to error: {e}")
        else:
            patoolib.extract_archive(str(file), outdir=output_dir.name, verbosity=-2)

        return output_dir

    def _diff_files(
        self,
        cmp: filecmp.dircmp[str],
        left_root: Optional[Path] = None,
        right_root: Optional[Path] = None,
    ) -> dict[str, tuple[Optional[str], Optional[str]]]:
        """
        Recursively compare files

        :param cmp:                                                 Dircmp to recursively compare
        :param left_root:                                           Left root to obtain the archive relative path

        :return: dict[str, tuple[Optional[str], Optional[str]]]     Dict with general name, left name and right name of files with different content
        :since: 1.0.0
        """

        # {general name: (actual name left, actual name right)}
        result: dict[str, tuple[Optional[str], Optional[str]]] = {}
        if not left_root:
            left_root = Path(cmp.left)
        if not right_root:
            right_root = Path(cmp.right)
        for name in cmp.left_only:
            if not (
                name.endswith(".log")
                and Path(cmp.left).joinpath(name.rstrip(".log")).is_file()
            ):
                actual_name = f"/{Path(cmp.left).relative_to(left_root).joinpath(name)}"
                general_name = self._arch.sub(
                    "ARCH", self._cname.sub("CNAME", actual_name)
                )
                result[general_name] = (actual_name, None)
        for name in cmp.right_only:
            if not (
                name.endswith(".log")
                and Path(cmp.right).joinpath(name.rstrip(".log")).is_file()
            ):
                actual_name = (
                    f"/{Path(cmp.right).relative_to(right_root).joinpath(name)}"
                )
                general_name = self._arch.sub(
                    "ARCH", self._cname.sub("CNAME", actual_name)
                )
                if general_name not in result:
                    result[general_name] = (None, actual_name)
                else:
                    result[general_name] = (result[general_name][0], actual_name)
        for name in cmp.diff_files:
            # Ignore *.log files as the timestamp differs always
            if not (
                name.endswith(".log")
                and Path(cmp.left).joinpath(name.rstrip(".log")).is_file()
            ):
                actual_name = f"/{Path(cmp.left).relative_to(left_root).joinpath(name)}"
                general_name = self._arch.sub(
                    "ARCH", self._cname.sub("CNAME", actual_name)
                )

                result[general_name] = (actual_name, actual_name)

        for sub_cmp in cmp.subdirs.values():
            result |= self._diff_files(
                sub_cmp, left_root=left_root, right_root=right_root
            )
        return result

    def generate(
        self, a: PathLike[str], b: PathLike[str]
    ) -> tuple[dict[str, Any], bool]:
        """
        Compare two .tar/.oci images with each other

        :param a:                       First .tar/.oci file
        :param b:                       Second .tar/.oci file

        :return: dict[str, Any], bool   Filtered recursive dict of paths with different content and flag indicating if whitelist was applied
        :since: 1.0.0
        """

        if filecmp.cmp(a, b, shallow=False):
            return {}, False

        with self._unpack(a) as unpacked_a, self._unpack(b) as unpacked_b:
            cmp = filecmp.dircmp(unpacked_a, unpacked_b, shallow=False)

            diff_files = self._diff_files(cmp)

            filtered: dict[tuple[str, Optional[str], Optional[str]], Any] = {
                (
                    general_name,
                    diff_files[general_name][0],
                    diff_files[general_name][1],
                ): {}
                for general_name in diff_files
                if not any(
                    re.match(pattern, general_name) for pattern in self.whitelist
                )
            }
            whitelist = len(diff_files) != len(filtered)

            result: dict[str, Any] = {}
            for general_name, left_name, right_name in filtered:
                result[general_name] = {}
                if left_name and right_name:
                    file_a = Path(unpacked_a).joinpath(left_name[1:])
                    file_b = Path(unpacked_b).joinpath(right_name[1:])
                    if (
                        file_a.is_file()
                        and file_b.is_file()
                        and patoolib.is_archive(file_a)
                        and patoolib.is_archive(file_b)
                    ):
                        filtered_rec, whitelist_rec = self.generate(file_a, file_b)
                        whitelist = whitelist or whitelist_rec
                        if filtered_rec != {}:
                            result[general_name] = filtered_rec
                        else:
                            # Remove if no files found in an archive to not count different timestamps inside the archives as a difference
                            del result[general_name]

        return result, whitelist
