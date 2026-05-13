# -*- coding: utf-8 -*-

"""
GitHub release notes generator
"""

import gzip
from collections import OrderedDict
from collections.abc import Mapping, MutableSequence
from io import BytesIO
from logging import Logger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional

import requests
import yaml

from ...apt import DebsrcFile
from ...constants import GL_DEB_REPO_BASE_URL, GLVD_BASE_URL, REQUESTS_TIMEOUTS
from ...features import CName
from ...flavors import Parser
from ...git import Repository
from ...logger import LoggerSetup
from ...s3 import S3Artifacts


class ReleaseImagesMetadata(object):
    """
    GitHub release instance to provide methods for interaction.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        version: str,
        commitish: str,
        s3_bucket_name: str,
        logger: Optional[Logger] = None,
    ):
        """
        Constructor __init__(Generator)

        :param repo: GitHub repository containing releases
        :param owner: GitHub owner for release data
        :param token: GitHub access token
        :param logger: Logger instance

        :since: 1.0.0
        """

        self._commitish = commitish
        self._flavors_parser: Optional[Parser] = None
        self._glvd_data: Optional[OrderedDict[str, Any]] = None
        self._s3_bucket_name = s3_bucket_name
        self._version = version

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.github")

        self._logger = logger

    @property
    def changes_and_cves_list(self) -> Dict[str, Any]:
        """
        Get list of fixed CVEs, grouped by upgraded package.

        Note: This result is not perfect, feel free to edit the generated release notes and
        file issues in glvd for improvement suggestions https://github.com/gardenlinux/glvd/issues
        """

        if self._glvd_data is None:
            try:
                response = self._raw_request(
                    "GET", f"{GLVD_BASE_URL}/releaseNotes/{self._version}"
                )
                data = response.json()
            except Exception as exn:
                self._logger.error(f"Failed to process GLVD API output: {exn}")
                data = {}

            if not isinstance(data, Mapping) or len(data.get("packageList", [])) < 1:
                return {}

            self._glvd_data = OrderedDict()

            for package in data["packageList"]:
                package_data = {
                    "version": {
                        "old": package["oldVersion"],
                        "new": package["newVersion"],
                    },
                    "fixed_cve_list": [],
                }

                if isinstance(package.get("fixedCves"), MutableSequence):
                    package_data["fixed_cve_list"] = package["fixedCves"]

                self._glvd_data[package["sourcePackageName"]] = package_data

        return self._glvd_data

    @property
    def flavors_parser(self) -> Parser:
        if self._flavors_parser is None:
            flavors_parser = None

            with TemporaryDirectory() as tmpdir:
                repo = Repository.checkout_repo_sparse(
                    tmpdir, ["flavors.yaml"], commit=self._commitish
                )
                flavors_file = Path(repo.root, "flavors.yaml")

                if not flavors_file.exists():
                    raise RuntimeError(f"Error: {flavors_file} does not exist.")

                # Load and validate the flavors.yaml
                with flavors_file.open("r") as fp:
                    flavors_parser = Parser(fp.read())

            if flavors_parser is None:
                raise RuntimeError(
                    f"Failed to find flavors for commitish: {self._commitish}"
                )

            self._flavors_parser = flavors_parser

        return self._flavors_parser

    @property
    def grouped_flavors_metadata(
        self,
    ) -> dict[str, dict[str, dict[str, list[dict[str, Any]]]]]:
        flavors = self.flavors_parser.filter(only_publish=True)

        # Group metadata by variant, platform, and architecture
        grouped_data: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = (
            OrderedDict()
        )

        s3_artifacts = S3Artifacts(self._s3_bucket_name)

        with TemporaryDirectory() as tmpdir:
            for flavor in flavors:
                self._logger.debug(
                    f"{flavor=} version={self._version} commitish={self._commitish}"
                )

                cname = CName(
                    flavor[1],
                    arch=flavor[0],
                    commit_hash=self._commitish,
                    version=self._version,
                )

                try:
                    release_object = list(
                        s3_artifacts.bucket.objects.filter(
                            Prefix=f"meta/singles/{cname.cname}"
                        )
                    )[0]

                    s3_artifacts.bucket.download_file(
                        release_object.key,
                        str(Path(tmpdir, f"{cname.cname}.s3_metadata.yaml")),
                    )
                except IndexError:
                    self._logger.warning(
                        f"No artifacts found for flavor {cname.cname}, skipping..."
                    )
                    continue

                with Path(tmpdir, f"{cname.cname}.s3_metadata.yaml").open("r") as file:
                    s3_data = ReleaseImagesMetadata.parse_s3_metadata(
                        yaml.load(file, Loader=yaml.SafeLoader)
                    )

                # Skip if no publishing metadata found
                if len(s3_data.get("published_image_metadata", [])) < 1:
                    continue

                if s3_data["variant_type"] not in grouped_data:
                    grouped_data[s3_data["variant_type"]] = {}
                if s3_data["platform"] not in grouped_data[s3_data["variant_type"]]:
                    grouped_data[s3_data["variant_type"]][s3_data["platform"]] = {}
                if (
                    s3_data["architecture"]
                    not in grouped_data[s3_data["variant_type"]][s3_data["platform"]]
                ):
                    grouped_data[s3_data["variant_type"]][s3_data["platform"]][
                        s3_data["architecture"]
                    ] = []

                grouped_data[s3_data["variant_type"]][s3_data["platform"]][
                    s3_data["architecture"]
                ].append(s3_data)

        return grouped_data

    @property
    def package_list(self) -> DebsrcFile:
        try:
            response = self._raw_request(
                "GET",
                f"{GL_DEB_REPO_BASE_URL}/dists/{self._version}/main/binary-amd64/Packages.gz",
            )
        except Exception as exn:
            self._logger.error(f"Failed to process Debian repository request: {exn}")
            return DebsrcFile()

        debsrc = DebsrcFile()

        with BytesIO(response.content) as buffer:
            with gzip.open(buffer, "rt") as file:
                debsrc.read(file)

        return debsrc

    def _raw_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Returns the requests response for the request given.

        :param method: Python requests method to call
        :param url: Python requests URL

        :return: (Response) Python requests response
        :since:  1.0.0
        """

        method_callable = getattr(requests, method.lower())

        response = method_callable(url, timeout=REQUESTS_TIMEOUTS, **kwargs)
        response.raise_for_status()

        return response  # type: ignore[no-any-return]

    @staticmethod
    def get_variant_from_metadata(metadata: Dict[str, Any]) -> str:
        feature_set = metadata.get("modifiers", [])

        if "_tpm2" in feature_set and "_trustedboot" in feature_set:
            return "trustedboot"
        elif "_usi" in feature_set:
            return "usi"
        else:
            return "legacy"

    @staticmethod
    def parse_s3_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        published_metadata = metadata.get("published_image_metadata", {})

        if not isinstance(published_metadata, Mapping):
            published_metadata = {}

        extended_metadata = metadata.copy()

        extended_metadata["variant_type"] = (
            ReleaseImagesMetadata.get_variant_from_metadata(metadata)
        )

        extended_metadata["published_image_metadata"] = published_metadata

        return extended_metadata
