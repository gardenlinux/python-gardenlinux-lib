# -*- coding: utf-8 -*-

"""
Artifact base name (ABN)
"""

import os
import re
from configparser import UNNAMED_SECTION, ConfigParser
from os import PathLike
from pathlib import Path
from typing import Optional, Self

from ..constants import (
    GL_BUG_REPORT_URL,
    GL_COMMIT_SPECIAL_VALUES,
    GL_DISTRIBUTION_NAME,
    GL_HOME_URL,
    GL_RELEASE_ID,
    GL_SUPPORT_URL,
    GL_VERSION_SPECIAL_VALUES,
)
from .versioned_flavor import VersionedFlavor


class ArtifactBaseName(VersionedFlavor):
    """
    Class to represent an artifact base name (ABN). It can be parsed from any
    file type.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        artifact: str,
    ):
        """
        Constructor __init__(ArtifactBaseName)

        :param artifact: Artifact name

        :since: 1.0.0
        """

        re_object = re.compile(
            "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)-([a-z0-9]+)-([a-z0-9.]+)-([a-z0-9]+)(\\.|$)"
        )

        re_match = re_object.match(artifact)

        assert re_match, f"Not a valid Garden Linux artifact: {artifact}"

        commit_id_or_hash = re_match[5]

        self._commit_id = commit_id_or_hash[:8]
        self._commit_hash = None

        if (
            len(commit_id_or_hash) == 40
            or commit_id_or_hash in GL_COMMIT_SPECIAL_VALUES
        ):  # sha1 hex
            self._commit_hash = commit_id_or_hash

        VersionedFlavor.__init__(self, re_match[1], re_match[3], re_match[4])

    @property
    def commit_hash(self) -> Optional[str]:
        """
        Returns the commit hash if part of the ABN parsed.

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
    def commit_id(self) -> str:
        """
        Returns the commit ID if part of the ABN parsed.

        :return: (str) Commit ID
        :since:  1.0.0
        """

        return self._commit_id

    @property
    def release_metadata_string(self) -> str:
        """
        Returns the release metadata describing the given ABN instance.

        :return: (str) Release metadata
        :since:  1.0.0
        """

        commit_hash = self.commit_hash
        commit_id = self.commit_id
        platform_variant = self.platform_variant
        version = self.version

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
VARIANT_ID="{self.flavor}"
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
    def version_and_commit_id(self) -> str:
        """
        Returns the version and commit ID of the ABN parsed.

        :return: (str) Version and commit ID
        :since:  1.0.0
        """

        return f"{self.version}-{self.commit_id}"

    def __str__(self) -> str:
        """
        Returns the Garden Linux artifact base name.

        :return: (str) Returns the ABN
        :since:  1.0.0
        """

        versioned_flavor = VersionedFlavor.__str__(self)
        versioned_flavor += f"-{self.commit_id}"

        return versioned_flavor

    def _copy_from_instance(self, artifact_base_name: Self) -> None:
        """
        Copies values from a given ABN instance.

        :param artifact_base_name: ABN instance

        :since: 1.0.0
        """

        VersionedFlavor._copy_from_instance(self, artifact_base_name)

        self._commit_hash = artifact_base_name.commit_hash
        self._commit_id = artifact_base_name.commit_id

    def load_from_release_file(self, release_file: PathLike[str] | str) -> None:
        """
        Loads and parses a release metadata file.

        :param release_file: Release metadata file

        :since: 1.0.0
        """

        artifact_base_name = self.__class__.new_from_release_file(release_file)

        if (
            artifact_base_name.flavor != self.flavor
            or (
                self._commit_id is not None
                and self._commit_id != artifact_base_name.commit_id
            )
            or (
                self._version is not None
                and self._version != artifact_base_name.version
            )
            or (
                not self._flag_frankenstein
                and artifact_base_name.platform
                not in artifact_base_name.feature_set_platform
            )
        ):
            raise RuntimeError(
                f"Release metadata file given is invalid: {release_file} failed consistency check - {self} != {artifact_base_name}"
            )

        self._copy_from_instance(artifact_base_name)

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
    def new_from_release_file(release_file: PathLike[str] | str) -> "ArtifactBaseName":
        """
        Loads and parses a release metadata file to return a new ABN instance.

        :param release_file: Release metadata file

        :return: (object) ABN instance
        :since:  1.0.0
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
            "VARIANT_ID",
            "GARDENLINUX_COMMIT_ID_LONG",
            "GARDENLINUX_FEATURES",
            "GARDENLINUX_PLATFORM",
            "GARDENLINUX_VERSION",
        ):
            if not release_config.has_option(UNNAMED_SECTION, release_field):
                raise RuntimeError(
                    f"Release metadata file given is invalid: {release_file} misses {release_field}"
                )

        artifact_base_name = release_config.get(UNNAMED_SECTION, "VARIANT_ID").strip(
            "\"'"
        )

        artifact_base_name += "-" + release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_VERSION"
        ).strip("\"'")

        artifact_base_name += "-" + release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID_LONG"
        ).strip("\"'")

        abn_object = ArtifactBaseName(artifact_base_name)

        abn_object._feature_set_cached = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_FEATURES"
        ).strip("\"'")

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_ELEMENTS"):
            abn_object._feature_elements_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_ELEMENTS")
                .strip("\"'")
                .split(",")
            )

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_FLAGS"):
            abn_object._feature_flags_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_FLAGS")
                .strip("\"'")
                .split(",")
            )

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES_PLATFORMS"):
            abn_object._feature_platforms_cached = (
                release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES_PLATFORMS")
                .strip("\"'")
                .split(",")
            )

        abn_object._platform_cached = release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_PLATFORM"
        ).strip("\"'")

        if release_config.has_option(UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"):
            abn_object._platform_variant_cached = release_config.get(
                UNNAMED_SECTION, "GARDENLINUX_PLATFORM_VARIANT"
            ).strip("\"'")

        return abn_object

    @staticmethod
    def get_version_and_commit_id_from_files(
        gardenlinux_root: Path | str,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Returns the version and commit ID based on files in the GardenLinux root directory.

        :param gardenlinux_root: GardenLinux root directory

        :return: (tuple) Version and commit ID if readable; None for both values otherwise
        :since:  1.0.0
        """

        if not isinstance(gardenlinux_root, PathLike):
            gardenlinux_root = Path(gardenlinux_root)

        commit_hash = None
        version = None

        if os.access(gardenlinux_root.joinpath("COMMIT"), os.R_OK):
            with gardenlinux_root.joinpath("COMMIT").open("r") as fp:
                commit_hash = fp.read().strip()[:8]

        if os.access(gardenlinux_root.joinpath("VERSION"), os.R_OK):
            with gardenlinux_root.joinpath("VERSION").open("r") as fp:
                version = fp.read().strip()

        if commit_hash is None or version is None:
            return (None, None)

        return (version, commit_hash)

    @staticmethod
    def new_instance(
        artifact_base_name: Optional[str] = None,
        versioned_flavor: Optional[str] = None,
        flavor: Optional[str] = None,
        cname: Optional[str] = None,
        arch: Optional[str] = None,
        version: Optional[str] = None,
        commit_id_or_hash: Optional[str] = None,
    ) -> "ArtifactBaseName":
        """
        Returns a new ABN instance based on various input data available.

        :param artifact_base_name: Artifact base name
        :param versioned_flavor: Garden Linux versioned flavor
        :param flavor: Garden Linux flavor
        :param cname: Garden Linux Ccanonical Name
        :param arch: Artifact architecture
        :param version: Artifact version
        :param commit_id_or_hash: Artifact commit ID or hash

        :return: (object) ABN instance
        :since:  1.0.0
        """

        if not artifact_base_name:
            if versioned_flavor:
                if not commit_id_or_hash:
                    raise ValueError("Argument missing: commit_id_or_hash")

                artifact_base_name = versioned_flavor + f"-{commit_id_or_hash}"
            elif flavor:
                if not version:
                    raise ValueError("Argument missing: version")
                if not commit_id_or_hash:
                    raise ValueError("Argument missing: commit_id_or_hash")

                artifact_base_name = flavor + f"-{version}-{commit_id_or_hash}"
            elif cname:
                if not arch:
                    raise ValueError("Argument missing: arch")
                if not version:
                    raise ValueError("Argument missing: version")
                if not commit_id_or_hash:
                    raise ValueError("Argument missing: commit_id_or_hash")

                artifact_base_name = cname + f"-{arch}-{version}-{commit_id_or_hash}"
            else:
                raise ValueError(
                    "Argument missing: At least one of artifact_base_name, cname, flavor or versioned_flavor"
                )

        abn_object = ArtifactBaseName(artifact_base_name)

        if cname and abn_object.cname != cname:
            raise RuntimeError("CName does not match the given argument")
        if arch and abn_object.arch != arch:
            raise RuntimeError("Architecture does not match the given argument")
        if (
            version
            and version not in GL_VERSION_SPECIAL_VALUES
            and abn_object.version != version
        ):
            raise RuntimeError("Version does not match the given argument")

        if commit_id_or_hash:
            if abn_object.commit_hash and abn_object.commit_hash != commit_id_or_hash:
                raise RuntimeError("Commit hash does not match the given argument")
            elif abn_object.commit_id != commit_id_or_hash:
                raise RuntimeError("Commit ID does not match the given argument")

        return abn_object
