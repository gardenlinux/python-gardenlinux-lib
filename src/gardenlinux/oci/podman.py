# -*- coding: utf-8 -*-

"""
OCI podman
"""

import json
import logging
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Dict, Optional

from .podman_context import PodmanContext
from ..logger import LoggerSetup


class Podman(object):
    """
    OCI podman provides access to an local podman installation.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.11.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Constructor __init__(Podman)

        :since: 0.11.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._logger = logger

    @PodmanContext.wrap
    def build(
        self,
        build_path: str,
        podman: PodmanContext,
        build_args: Dict[str, str] = None,
        oci_tag: str = None,
        log_build_output: bool = False,
        **kwargs,
    ):
        if isinstance(build_args, Mapping):
            kwargs["buildargs"] = build_args

        if oci_tag is not None:
            kwargs["tag"] = oci_tag

        image, log = podman.images.build(path=build_path, dockerfile="Containerfile", **kwargs)

        if log_build_output:
            for line in log:
                self._logger.info(json.loads(line)['stream'].strip())

        return image.id

    @PodmanContext.wrap
    def build_and_save_oci_archive(
        self,
        build_path: str,
        oci_archive_file_name: str | PathLike[str],
        podman: PodmanContext,
        build_args: Dict[str, str] = None,
        oci_tag: str = None,
        log_build_output: bool = False,
        **kwargs,
    ):
        oci_archive_file_name = Path(oci_archive_file_name)

        image_id = self.build(build_path, podman=podman, build_args=build_args, oci_tag=oci_tag)
        self.save_oci_archive(image_id, oci_archive_file_name, podman=podman)

        return {oci_archive_file_name.name: image_id}

    @PodmanContext.wrap
    def load_oci_archives_from_directory(
        self, oci_dir: str | PathLike[str], /, podman: PodmanContext
    ) -> Dict[str, str]:
        oci_archives = {}
        oci_dir = Path(oci_dir)

        for oci_archive in oci_dir.iterdir():
            if not oci_archive.match("*.oci"):
                continue

            image = next(podman.images.load(file_path=oci_archive))
            oci_archives[oci_archive.name] = image.id

        return oci_archives

    @PodmanContext.wrap
    def save_oci_archive(
        self,
        image_id: str,
        oci_archive_file_name: str | PathLike[str],
        podman: PodmanContext,
        oci_tag: str = None,
    ):
        oci_archive_file_name = Path(oci_archive_file_name)

        if oci_archive_file_name.exists():
            raise RuntimeError("OCI archive file does already exist")

        image = podman.images.get(image_id)

        with oci_archive_file_name.open("wb") as fp:
            named = True

            if oci_tag is not None:
                named = oci_tag

            for chunk in image.save(named=named):
                fp.write(chunk)
