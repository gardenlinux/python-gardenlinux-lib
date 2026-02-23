# -*- coding: utf-8 -*-

"""
Canonical name (cname)
"""

import re
from configparser import UNNAMED_SECTION, ConfigParser
from os import PathLike, environ
from pathlib import Path
from typing import Any, Dict, List, Optional, Self

from ..constants import (
    ARCHS,
    GL_BUG_REPORT_URL,
    GL_DISTRIBUTION_NAME,
    GL_HOME_URL,
    GL_PLATFORM_FRANKENSTEIN,
    GL_RELEASE_ID,
    GL_SUPPORT_URL,
)
from .parser import Parser


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
        self._feature_platforms_cached: Optional[List[str]] = None
        self._feature_set_cached: Optional[str] = None
        self._features_cached: Optional[Dict[str, Any]] = None
        self._platform_cached: Optional[str] = None
        self._platform_variant_cached: Optional[str] = None
        self._flavor = ""
        self._version = None

        self._flag_frankenstein = bool(environ.get("GL_ALLOW_FRANKENSTEIN", False))

        self._flag_multiple_platforms = bool(
            environ.get("GL_ALLOW_MULTIPLE_PLATFORMS", False)
        )

        if self._flag_frankenstein:
            self._flag_multiple_platforms = True

        commit_id_or_hash = None

        if version is not None:
            # Support version values formatted as <version>-<commit_hash>
            if commit_hash is None:
                re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", version)
                assert re_match, f"Not a valid version {version}"

                commit_id_or_hash = re_match[3]
                version = re_match[1]
            else:
                commit_id_or_hash = commit_hash

        re_object = re.compile(
            "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$"
        )

        re_match = re_object.match(cname)

        # Workaround Garden Linux canonical names without mandatory final commit hash
        if (
            not re_match
            and commit_id_or_hash
            and re.match(
                "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+))*)?$",
                cname,
            )
        ):
            re_match = re_object.match(f"{cname}-{commit_id_or_hash}")

        assert re_match, f"Not a valid Garden Linux canonical name {cname}"

        if re_match.lastindex == 1:
            self._flavor = re_match[1]
        else:
            if commit_id_or_hash is None:
                commit_id_or_hash = re_match[7]
            elif re_match.group(7) is not None:
                assert commit_id_or_hash.startswith(re_match[7]), (
                    f"Mismatch between Garden Linux canonical name '{cname}' and given commit ID '{commit_id_or_hash}' detected"
                )

            self._flavor = re_match[1]
            self._version = re_match[6]

            if re_match[4] in ARCHS:
                self._arch = re_match[4]
            else:
                self._flavor += re_match[3]

        if self._arch is None and arch is not None:
            self._arch = arch

        if version is not None:
            if self._version is None:
                self._version = version
            else:
                assert version == self._version, (
                    f"Mismatch between Garden Linux canonical name '{cname}' and given version '{version}' detected"
                )

        if commit_id_or_hash is not None:
            self._commit_id = commit_id_or_hash[:8]

            if len(commit_id_or_hash) == 40 or commit_id_or_hash == "local":  # sha1 hex
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
    def commit_hash(self) -> Optional[str]:
        """
        Returns the commit hash if part of the cname parsed.

        :return: (str) Commit hash
        :since:  1.0.0
        """

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
    def features(self) -> Dict[str, Any]:
        """
        Returns the features for the cname parsed.

        :return: (dict) Features of the cname
        :since:  0.10.14
        """

        if self._features_cached is None:
            self._features_cached = Parser().filter_as_dict(self.flavor)

        return self._features_cached

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

        return ",".join(self.features["element"])

    @property
    def feature_set_flag(self) -> str:
        """
        Returns the feature set of type "flag" for the cname parsed.

        :return: (str) Feature set flags
        :since:  1.0.0
        """

        if self._feature_flags_cached is not None:
            return ",".join(self._feature_flags_cached)

        return ",".join(self.features["flag"])

    @property
    def feature_set_platform(self) -> str:
        """
        Returns the feature set of type "platform" for the cname parsed.

        :return: (str) Feature set platform
        :since:  1.0.0
        """

        if self._feature_platforms_cached is None:
            platforms = self.features["platform"]
        else:
            platforms = self._feature_platforms_cached

        if self._flag_multiple_platforms:
            return ",".join(platforms)

        assert len(platforms) < 2
        "Only one platform is supported"
        return platforms[0]  # type: ignore[no-any-return]

    @property
    def feature_set_list(self) -> List[str]:
        """
        Returns the feature set for the cname parsed.

        :return: (list) Feature set list of the cname
        :since:  0.10.12
        """

        if self._feature_set_cached is not None:
            return self._feature_set_cached.split(",")

        return Parser().filter_as_list(self.flavor)

    @property
    def platform(self) -> str:
        """
        Returns the platform for the cname parsed.

        :return: (str) Platform
        :since:  0.7.0
        """

        if self._platform_cached is not None:
            platforms = [self._platform_cached]
        elif self._feature_platforms_cached is not None:
            platforms = self._feature_platforms_cached
        else:
            platforms = self.features["platform"]

        if self._flag_frankenstein and len(platforms) > 1:
            return GL_PLATFORM_FRANKENSTEIN

        if not self._flag_multiple_platforms:
            assert len(platforms) < 2
            "Only one platform is supported"

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

        commit_hash = self.commit_hash
        commit_id = self.commit_id
        platform_variant = self.platform_variant
        version = self.version

        if commit_id is None:
            commit_id = ""

        if commit_hash is None:
            commit_hash = commit_id

        if platform_variant is None:
            platform_variant = ""

        if version is None:
            pretty_name = f"{GL_DISTRIBUTION_NAME} unsupported version"
            version = ""
        else:
            pretty_name = f"{GL_DISTRIBUTION_NAME} {version}"

        metadata = f"""
ID={GL_RELEASE_ID}
ID_LIKE=debian
NAME="{GL_DISTRIBUTION_NAME}"
PRETTY_NAME="{pretty_name}"
IMAGE_VERSION={version}
VARIANT_ID="{self.flavor}-{self.arch}"
HOME_URL="{GL_HOME_URL}"
SUPPORT_URL="{GL_SUPPORT_URL}"
BUG_REPORT_URL="{GL_BUG_REPORT_URL}"
GARDENLINUX_CNAME="{self.cname}"
GARDENLINUX_FEATURES="{self.feature_set}"
GARDENLINUX_FEATURES_PLATFORMS="{self.feature_set_platform}"
GARDENLINUX_FEATURES_ELEMENTS="{self.feature_set_element}"
GARDENLINUX_FEATURES_FLAGS="{self.feature_set_flag}"
GARDENLINUX_PLATFORM="{self.platform}"
GARDENLINUX_PLATFORM_VARIANT="{platform_variant}"
GARDENLINUX_VERSION="{version}"
GARDENLINUX_COMMIT_ID="{commit_id}"
GARDENLINUX_COMMIT_ID_LONG="{commit_hash}"
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

        if self._version is None or self._commit_id is None:
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

    def _copy_from_cname_object(self, cname_object: Self) -> None:
        """
        Copies values from a given Garden Linux canonical name instance.

        :param cname_object: Garden Linux canonical name instance

        :since: 1.0.0
        """

        self._arch = cname_object.arch
        self._commit_hash = cname_object.commit_hash
        self._commit_id = cname_object.commit_id
        self._feature_set_cached = cname_object.feature_set
        self._feature_elements_cached = cname_object.feature_set_element.split(",")
        self._feature_flags_cached = cname_object.feature_set_flag.split(",")
        self._feature_platforms_cached = cname_object.feature_set_platform.split(",")
        self._platform_cached = cname_object.platform
        self._platform_variant_cached = cname_object.platform_variant
        self._version = cname_object.version

    def load_from_release_file(self, release_file: PathLike[str] | str) -> None:
        """
        Loads and parses a release metadata file.

        :param release_file: Release metadata file

        :since: 1.0.0
        """

        cname_object = CName.new_from_release_file(release_file)

        if (
            cname_object.flavor != self.flavor
            or (
                self._commit_id is not None
                and self._commit_id != cname_object.commit_id
            )
            or (self._version is not None and self._version != cname_object.version)
            or (
                not self._flag_frankenstein
                and cname_object.platform not in cname_object.feature_set_platform
            )
        ):
            raise RuntimeError(
                f"Release metadata file given is invalid: {release_file} failed consistency check - {self.cname} != {cname_object.cname}"
            )

        self._copy_from_cname_object(cname_object)

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
    def new_from_release_file(release_file: PathLike[str] | str) -> "CName":
        """
        Loads and parses a release metadata file.

        :param release_file: Release metadata file

        :since: 0.10.10
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
            "GARDENLINUX_COMMIT_ID_LONG",
            "GARDENLINUX_FEATURES",
            "GARDENLINUX_PLATFORM",
            "GARDENLINUX_VERSION",
        ):
            if not release_config.has_option(UNNAMED_SECTION, release_field):
                raise RuntimeError(
                    f"Release metadata file given is invalid: {release_file} misses {release_field}"
                )

        commit_hash = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID_LONG"
        ).strip("\"'")

        version = release_config.get(UNNAMED_SECTION, "GARDENLINUX_VERSION").strip(
            "\"'"
        )

        cname_object = CName(
            release_config.get(UNNAMED_SECTION, "GARDENLINUX_CNAME").strip("\"'"),
            commit_hash=commit_hash,
            version=version,
        )

        cname_object._feature_set_cached = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_FEATURES"
        ).strip("\"'")

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_ELEMENTS"):
            cname_object._feature_elements_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_ELEMENTS")
                .strip("\"'")
                .split(",")
            )

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_FLAGS"):
            cname_object._feature_flags_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_FLAGS")
                .strip("\"'")
                .split(",")
            )

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_PLATFORMS"):
            cname_object._feature_platforms_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_PLATFORMS")
                .strip("\"'")
                .split(",")
            )

        cname_object._platform_cached = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_PLATFORM"
        ).strip("\"'")

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"):
            cname_object._platform_variant_cached = release_config.get(
                UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"
            ).strip("\"'")

        return cname_object
