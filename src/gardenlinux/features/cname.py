# -*- coding: utf-8 -*-

"""
Canonical name (cname)
"""

import re
from configparser import UNNAMED_SECTION, ConfigParser
from os import PathLike, environ
from pathlib import Path
from typing import List, Optional

from ..constants import (
    ARCHS,
    GL_BUG_REPORT_URL,
    GL_DISTRIBUTION_NAME,
    GL_HOME_URL,
    GL_RELEASE_ID,
    GL_SUPPORT_URL,
)
from .parser import Parser

RE_CAMEL_CASE_SPLITTER = re.compile("([A-Z]+|[a-z0-9])([A-Z])(?!$)")
"""
CamelCase splitter RegExp
"""


class CName(object):
    """
    Class to represent a canonical name (cname).

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        cname: str,
        arch: Optional[str] = None,
        commit_hash: Optional[str] = None,
        version: Optional[str] = None,
    ):
        """
        Constructor __init__(CName)

        :param cname:     Canonical name to represent
        :param arch:      Architecture if not part of cname
        :param commit_hash: Commit ID or hash if not part of cname
        :param version:   Version if not part of cname

        :since: 0.7.0
        """

        self._arch = None
        self._commit_hash = None
        self._commit_id = None
        self._feature_elements_cached: Optional[List[str]] = None
        self._feature_flags_cached: Optional[List[str]] = None
        self._feature_platform_cached: Optional[str] = None
        self._feature_set_cached: Optional[str] = None
        self._platform_variant_cached: Optional[str] = None
        self._flag_multiple_platforms = bool(
            environ.get("GL_ALLOW_FRANKENSTEIN", False)
        )
        self._flavor = ""
        self._version = None

        commit_id_or_hash = None

        re_match = re.match(
            "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
            cname,
        )

        assert re_match, f"Not a valid GardenLinux canonical name {cname}"

        if re_match.lastindex == 1:
            self._flavor = re_match[1]
        else:
            commit_id_or_hash = re_match[7]
            self._flavor = re_match[1]
            self._version = re_match[6]

            if re_match[4] in ARCHS:
                self._arch = re_match[4]
            else:
                self._flavor += re_match[3]

        if self._arch is None and arch is not None:
            self._arch = arch

        if self._version is None and version is not None:
            # Support version values formatted as <version>-<commit_hash>
            if commit_hash is None:
                re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", version)
                assert re_match, f"Not a valid version {version}"

                commit_id_or_hash = re_match[3]
                self._version = re_match[1]
            else:
                commit_id_or_hash = commit_hash
                self._version = version

        if commit_id_or_hash is not None:
            self._commit_id = commit_id_or_hash[:8]

            if len(commit_id_or_hash) == 40:  # sha1 hex
                self._commit_hash = commit_id_or_hash

    @property
    def arch(self) -> Optional[str]:
        """
        Returns the architecture for the cname parsed.

        :return: (str) CName architecture
        :since:  0.7.0
        """

        return self._arch

    @property
    def cname(self) -> str:
        """
        Returns the cname parsed.

        :return: (str) CName
        :since:  0.7.0
        """

        cname = self._flavor

        if self._arch is not None:
            cname += f"-{self._arch}"

        if self._commit_id is not None and self._version is not None:
            cname += f"-{self.version_and_commit_id}"

        return cname

    @property
    def commit_hash(self) -> str:
        """
        Returns the commit hash if part of the cname parsed.

        :return: (str) Commit hash
        :since:  1.0.0
        """

        if self._commit_hash is None:
            raise RuntimeError(
                "GardenLinux canonical name given does not contain the commit hash"
            )

        return self._commit_hash

    @commit_hash.setter
    def commit_hash(self, commit_hash: str) -> None:
        """
        Sets the commit hash

        :param commit_hash: Commit hash

        :since: 1.0.0
        """

        if self._commit_id is not None and not commit_hash.startswith(self._commit_id):
            raise RuntimeError("Commit hash given differs from commit ID already set")

        self._commit_id = commit_hash[:8]
        self._commit_hash = commit_hash

    @property
    def commit_id(self) -> Optional[str]:
        """
        Returns the commit ID if part of the cname parsed.

        :return: (str) Commit ID
        :since:  0.7.0
        """

        return self._commit_id

    @property
    def flavor(self) -> str:
        """
        Returns the flavor for the cname parsed.

        :return: (str) Flavor
        :since:  0.7.0
        """

        return self._flavor

    @property
    def feature_set(self) -> str:
        """
        Returns the feature set for the cname parsed.

        :return: (str) Feature set of the cname
        :since:  0.7.0
        """

        if self._feature_set_cached is not None:
            return self._feature_set_cached

        return Parser().filter_as_string(self.flavor)

    @property
    def feature_set_element(self) -> str:
        """
        Returns the feature set of type "element" for the cname parsed.

        :return: (str) Feature set elements
        :since:  1.0.0
        """

        if self._feature_elements_cached is not None:
            return ",".join(self._feature_elements_cached)

        return ",".join(Parser().filter_as_dict(self.flavor)["element"])

    @property
    def feature_set_flag(self) -> str:
        """
        Returns the feature set of type "flag" for the cname parsed.

        :return: (str) Feature set flags
        :since:  1.0.0
        """

        if self._feature_flags_cached is not None:
            return ",".join(self._feature_flags_cached)

        return ",".join(Parser().filter_as_dict(self.flavor)["flag"])

    @property
    def feature_set_platform(self) -> str:
        """
        Returns the feature set of type "platform" for the cname parsed.

        :return: (str) Feature set platform
        :since:  1.0.0
        """

        if self._feature_platforms_cached is None:
            platforms = Parser().filter_as_dict(self.flavor)["platform"]
        else:
            platforms = self._feature_platforms_cached

        if self._flag_multiple_platforms:
            return ",".join(platforms)

        assert len(platforms) < 2
        "Only one platform is supported"
        return platforms[0]

    @property
    def platform(self) -> str:
        """
        Returns the feature set of type "platform" for the cname parsed.

        :return: (str) Feature set platforms
        :since:  0.7.0
        """

        if self._feature_platforms_cached is None:
            platforms = Parser().filter_as_dict(self.flavor)["platform"]
        else:
            platforms = self._feature_platforms_cached

        if not self._flag_multiple_platforms:
            assert len(platforms) < 2

        return platforms[0]

    @property
    def platform_variant(self) -> Optional[str]:
        """
        Returns the platform variant for the cname parsed.

        :return: (str) Platform variant
        :since:  1.0.0
        """

        if self._platform_variant_cached is not None:
            return self._platform_variant_cached

        # @TODO: Platform variant is set by GardenLinux features to the release file. If not read or cached it is currently invisible for this library.
        return None

    @platform_variant.setter
    def platform_variant(self, variant: str) -> None:
        """
        Sets the the platform variant

        :param variant: Platform variant

        :since: 1.0.0
        """

        self._platform_variant_cached = variant

    @property
    def release_metadata_string(self) -> str:
        """
        Returns the release metadata describing the given CName instance.

        :return: (str) Release metadata describing the given CName instance
        :since:  1.0.0
        """

        features = Parser().filter_as_dict(self.flavor)

        if not self._flag_multiple_platforms:
            assert len(features["platform"]) < 2
            "Only one platform is supported"

        elements = ",".join(features["element"])
        flags = ",".join(features["flag"])
        platform = features["platform"][0]
        platforms = ",".join(features["platform"])
        platform_variant = self.platform_variant

        if platform_variant is None:
            platform_variant = ""

        metadata = f"""
ID={GL_RELEASE_ID}
ID_LIKE=debian
NAME="{GL_DISTRIBUTION_NAME}"
PRETTY_NAME="{GL_DISTRIBUTION_NAME} {self.version}"
IMAGE_VERSION={self.version}
VARIANT_ID="{self.flavor}-{self.arch}"
HOME_URL="{GL_HOME_URL}"
SUPPORT_URL="{GL_SUPPORT_URL}"
BUG_REPORT_URL="{GL_BUG_REPORT_URL}"
GARDENLINUX_CNAME="{self.cname}"
GARDENLINUX_FEATURES="{self.feature_set}"
GARDENLINUX_FEATURES_PLATFORMS="{platforms}"
GARDENLINUX_FEATURES_ELEMENTS="{elements}"
GARDENLINUX_FEATURES_FLAGS="{flags}"
GARDENLINUX_PLATFORM="{platform}"
GARDENLINUX_PLATFORM_VARIANT="{platform_variant}"
GARDENLINUX_VERSION="{self.version}"
GARDENLINUX_COMMIT_ID="{self.commit_id}"
GARDENLINUX_COMMIT_ID_LONG="{self.commit_hash}"
        """.strip()

        return metadata

    @property
    def version(self) -> Optional[str]:
        """
        Returns the version if part of the cname parsed.

        :return: (str) Version
        :since:  0.7.0
        """

        return self._version

    @property
    def version_and_commit_id(self) -> Optional[str]:
        """
        Returns the version and commit ID if part of the cname parsed.

        :return: (str) Version and commit ID
        :since:  0.7.0
        """

        if self._commit_id is None:
            return None

        return f"{self._version}-{self._commit_id}"

    @property
    def version_epoch(self) -> Optional[int]:
        """
        Returns the GardenLinux version epoch of the cname parsed.

        :return: (str) GardenLinux version epoch
        :since:  1.0.0
        """

        epoch = None

        if self._version is not None and "." in self._version:
            epoch = int(self._version.split(".", 1)[0])

        return epoch

    def load_from_release_file(self, release_file: PathLike[str] | str) -> None:
        """
        Loads and parses a release metadata file.

        :param release_file: Release metadata file

        :since: 1.0.0
        """

        if not isinstance(release_file, PathLike):
            release_file = Path(release_file)

        if not release_file.exists():  # type: ignore[attr-defined]
            raise RuntimeError(
                f"Release metadata file given is invalid: {release_file}"
            )

        release_config = ConfigParser(allow_unnamed_section=True)
        release_config.read(release_file)

        for release_field in (
            "GARDENLINUX_CNAME",
            "GARDENLINUX_FEATURES",
            "GARDENLINUX_FEATURES_ELEMENTS",
            "GARDENLINUX_FEATURES_FLAGS",
            "GARDENLINUX_FEATURES_PLATFORMS",
            "GARDENLINUX_VERSION",
        ):
            if not release_config.has_option(UNNAMED_SECTION, release_field):
                raise RuntimeError(
                    f"Release metadata file given is invalid: {release_file} misses {release_field}"
                )

        loaded_cname_instance = CName(
            release_config.get(UNNAMED_SECTION, "GARDENLINUX_CNAME").strip("\"'")
        )

        commit_id = release_config.get(UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID").strip(
            "\"'"
        )

        commit_hash = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID_LONG"
        ).strip("\"'")

        version = release_config.get(UNNAMED_SECTION, "GARDENLINUX_VERSION").strip(
            "\"'"
        )

        if (
            loaded_cname_instance.flavor != self.flavor
            or loaded_cname_instance.commit_id != commit_id
            or (self._commit_id is not None and self._commit_id != commit_id)
            or loaded_cname_instance.version != version
            or (self._version is not None and self._version != version)
        ):
            raise RuntimeError(
                f"Release metadata file given is invalid: {release_file} failed consistency check - {self.cname} != {loaded_cname_instance.cname}"
            )

        self._arch = loaded_cname_instance.arch
        self._flavor = loaded_cname_instance.flavor
        self._commit_hash = commit_hash
        self._commit_id = commit_id
        self._version = version

        self._feature_set_cached = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_FEATURES"
        ).strip("\"'")

        self._feature_elements_cached = (
            release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_ELEMENTS")
            .strip("\"'")
            .split(",")
        )

        self._feature_flags_cached = (
            release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_FLAGS")
            .strip("\"'")
            .split(",")
        )

        self._feature_platforms_cached = (
            release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_PLATFORMS")
            .strip("\"'")
            .split(",")
        )

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"):
            self._platform_variant_cached = release_config.get(
                UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"
            ).strip("\"'")

    def save_to_release_file(
        self, release_file: PathLike[str] | str, overwrite: Optional[bool] = False
    ) -> None:
        """
        Saves the release metadata file.

        :param release_file: Release metadata file

        :since: 1.0.0
        """

        if not isinstance(release_file, PathLike):
            release_file = Path(release_file)

        if not overwrite and release_file.exists():  # type: ignore[attr-defined]
            raise RuntimeError(
                f"Refused to overwrite existing release metadata file: {release_file}"
            )

        with release_file.open("w") as fp:  # type: ignore[attr-defined]
            fp.write(self.release_metadata_string)

    @staticmethod
    def get_camel_case_name_for_feature(feature, char = "_"):
        return RE_CAMEL_CASE_SPLITTER.sub(f"\\1{char}\\2", feature).lower()
