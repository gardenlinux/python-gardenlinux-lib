# -*- coding: utf-8 -*-

"""
OCI podman
"""

import json
import logging
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..logger import LoggerSetup
from .podman_context import PodmanContext


class Podman(object):
    """
    OCI podman provides access to an local podman installation.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self, insecure: Optional[bool] = False, logger: Optional[logging.Logger] = None
    ):
        """
        Constructor __init__(Podman)

        :since: 1.0.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._insecure = insecure
        self._logger = logger

    @PodmanContext.wrap
    def build(
        self,
        build_path: str,
        podman: PodmanContext,
        platform: Optional[str] = None,
        build_args: Optional[Dict[str, str]] = None,
        oci_tag: Optional[str] = None,
        log_build_output: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Build a container.

        :since: 1.0.0
        """

        if not Path(build_path, "Containerfile").exists():
            raise RuntimeError(f"No Containerfile found at: {build_path}")

        if isinstance(build_args, Mapping):
            kwargs["buildargs"] = build_args

        if platform is not None:
            kwargs["platform"] = platform

        if oci_tag is not None:
            kwargs["tag"] = oci_tag

        image, log = podman.images.build(
            path=build_path, dockerfile="Containerfile", **kwargs
        )

        if log_build_output:
            for line in log:
                self._logger.info(json.loads(line)["stream"].strip())

        return image.id  # type: ignore[no-any-return]

    @PodmanContext.wrap
    def build_and_save_oci_archive(
        self,
        build_path: str,
        oci_archive_file_name: str | PathLike[str],
        podman: PodmanContext,
        platform: Optional[str] = None,
        build_args: Optional[Dict[str, str]] = None,
        oci_tag: Optional[str] = None,
        log_build_output: bool = False,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """
        Build a container and save the result as an OCI archive with the given path and file name.

        :since: 1.0.0
        """

        oci_archive_file_name = Path(oci_archive_file_name)

        image_id = self.build(
            build_path,
            podman=podman,
            platform=platform,
            build_args=build_args,
            oci_tag=oci_tag,
            log_build_output=log_build_output,
        )

        self.save_oci_archive(image_id, oci_archive_file_name, podman=podman)

        return {oci_archive_file_name.name: image_id}

    @PodmanContext.wrap
    def get_image_id(
        self,
        container: str,
        podman: PodmanContext,
        oci_tag: Optional[str] = None,
    ) -> str:
        """
        Returns the Podman image ID for a given OCI container tag.

        :since: 1.0.0
        """

        container_tag = container

        if oci_tag is not None:
            if ":" in oci_tag:
                container_tag = oci_tag
            else:
                container_tag += f":{oci_tag}"

        image = podman.images.get(container_tag)
        return image.id  # type: ignore[no-any-return]

    @PodmanContext.wrap
    def load_oci_archive(
        self, oci_archive_file_name: str | PathLike[str], /, podman: PodmanContext
    ) -> str:
        """
        Load OCI archives from the given directory.

        :since: 1.0.0
        """

        oci_archive_file_name = Path(oci_archive_file_name)

        image = next(podman.images.load(file_path=oci_archive_file_name))
        return image.id  # type: ignore[no-any-return]

    @PodmanContext.wrap
    def load_oci_archives_from_directory(
        self, oci_dir: str | PathLike[str], /, podman: PodmanContext
    ) -> Dict[str, str]:
        """
        Load OCI archives from the given directory.

        :since: 1.0.0
        """

        oci_archives = {}
        oci_dir = Path(oci_dir)

        for oci_archive in oci_dir.iterdir():
            if not oci_archive.match("*.oci"):
                continue

            image = next(podman.images.load(file_path=oci_archive))
            oci_archives[oci_archive.name] = image.id

        return oci_archives

    @PodmanContext.wrap
    def pull(
        self,
        container: str,
        podman: PodmanContext,
        platform: Optional[str] = None,
        oci_tag: Optional[str] = None,
    ) -> None:
        """
        Pulls a given OCI container.

        :since: 1.0.0
        """

        kwargs: Dict[str, Any] = {}

        if self._insecure:
            kwargs["tlsVerify"] = False

        if platform is not None:
            kwargs["platform"] = platform

        if oci_tag is not None:
            kwargs["tag"] = oci_tag

        podman.images.pull(container, **kwargs)

    @PodmanContext.wrap
    def push(
        self,
        container: str,
        podman: PodmanContext,
        destination: Optional[str] = None,
        oci_tag: Optional[str] = None,
    ) -> None:
        """
        Pushs a given OCI container.

        :since: 1.0.0
        """

        kwargs: Dict[str, Any] = {}

        if self._insecure:
            kwargs["tlsVerify"] = False

        if destination is not None:
            kwargs["destination"] = destination

        if oci_tag is not None:
            kwargs["tag"] = oci_tag

        podman.images.push(container, **kwargs)

    @PodmanContext.wrap
    def save_oci_archive(
        self,
        image_id: str,
        oci_archive_file_name: str | PathLike[str],
        podman: PodmanContext,
        oci_tag: Optional[str] = None,
    ) -> None:
        """
        Save the given Podman image ID as an OCI archive with the given path and
        file name.

        :since: 1.0.0
        """

        oci_archive_file_name = Path(oci_archive_file_name)

        if oci_archive_file_name.exists():
            raise RuntimeError("OCI archive file does already exist")

        image = podman.images.get(image_id)

        with oci_archive_file_name.open("wb") as fp:
            named: bool | str = True

            if oci_tag is not None:
                if oci_tag not in image.tags:
                    self.tag(image.id, oci_tag, podman=podman)

                named = oci_tag

            for chunk in image.save(named=named):
                fp.write(chunk)

    @PodmanContext.wrap
    def tag(
        self,
        image_id: str,
        oci_container_tag: str,
        podman: PodmanContext,
    ) -> None:
        """
        Tags a given Podman image ID with the container tag given.

        :since: 1.0.0
        """

        oci_data = oci_container_tag.rsplit(":", 1)

        if len(oci_data) < 2:
            raise RuntimeError("No tag given")

        image = podman.images.get(image_id)
        image.tag(oci_data[0], oci_data[1])

    @PodmanContext.wrap
    def tag_list(
        self,
        image_id: str,
        oci_container_tags_list: List[str],
        podman: PodmanContext,
    ) -> None:
        """
        Tags a given Podman image ID with the list of container tags given.

        :since: 1.0.0
        """

        for container_tag in oci_container_tags_list:
            self.tag(image_id, container_tag, podman=podman)

    @staticmethod
    def get_container_tag_list(container: str, tag_list: Sequence[str]) -> List[str]:
        """
        Returns a list of "container:tag" values.

        :since: 1.0.0
        """

        container_tag_list = []

        if isinstance(tag_list, Sequence):
            for tag in tag_list:
                if ":" in tag:
                    container_tag_list.append(tag)
                else:
                    container_tag_list.append(f"{container}:{tag}")

        return container_tag_list

    @staticmethod
    def parse_build_args_list(args_list: List[str]) -> Dict[str, str]:
        """
        Returns a mapping of build arguments based on the given list.

        :since: 1.0.0
        """

        args = {}

        for arg_line in args_list:
            arg_data = arg_line.split("=", 1)

            if len(arg_data) < 2:
                raise RuntimeError(f"Failed to parse build argument: {arg_line}")

            args[arg_data[0]] = arg_data[1]

        return args
