# -*- coding: utf-8 -*-

"""
OCI manifest
"""

import json
from collections.abc import Mapping
from copy import deepcopy
from hashlib import sha256
from typing import Any, Dict

from oras.defaults import annotation_title as ANNOTATION_TITLE

from ..constants import COMMIT_HASH_LENGTH, COMMIT_ID_LENGTH
from .schemas import empty_manifest_metadata


class Manifest(dict):  # type: ignore[type-arg]
    """
    OCI manifest

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    ANNOTATION_COMMIT_KEY = "io.gardenlinux.manifest.commit"
    """
    OCI image manifest GardenLinux commit hash annotation
    """
    ANNOTATION_COMMIT_DEPRECATED_KEY = "commit"
    """
    OCI image manifest GardenLinux commit hash deprecated annotation
    """
    ANNOTATION_DESCRIPTION_KEY = "org.opencontainers.image.description"
    """
    OCI image manifest description annotation
    """
    ANNOTATION_TITLE_KEY = ANNOTATION_TITLE
    """
    OCI image manifest title annotation
    """
    ANNOTATION_VERSION_KEY = "io.gardenlinux.manifest.version"
    """
    OCI image manifest GardenLinux version annotation
    """
    ANNOTATION_VERSION_DEPRECATED_KEY = "version"
    """
    OCI image manifest GardenLinux version deprecated annotation
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Constructor __init__(Manifest)

        :since: 0.7.0
        """

        dict.__init__(self)

        self.update(deepcopy(empty_manifest_metadata))

        for arg in args:
            if not isinstance(arg, Mapping):
                raise TypeError("Arguments given to Manifest are invalid")

            self.update(arg)

        self.update(**kwargs)

    @property
    def commit(self) -> str:
        """
        Returns the GardenLinux Git commit hash of the OCI manifest.

        :return: (str) OCI GardenLinux Git commit hash
        :since:  0.7.0
        """

        annotation_commit_key = self.__class__.ANNOTATION_COMMIT_KEY

        if annotation_commit_key not in self.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected manifest with missing annotation '{annotation_commit_key}' found"
            )

        return self["annotations"][annotation_commit_key]  # type: ignore[no-any-return]

    @commit.setter
    def commit(self, value: str) -> None:
        """
        Sets the GardenLinux Git commit hash of the OCI manifest.

        :param value: OCI GardenLinux Git commit hash

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"][self.__class__.ANNOTATION_COMMIT_KEY] = value

    @property
    def commit_id(self) -> str:
        """
        Returns the GardenLinux Git commit ID of the OCI manifest.

        :return: (str) OCI GardenLinux Git commit ID
        :since:  1.0.8
        """

        commit_id = self.commit

        if len(commit_id) == COMMIT_HASH_LENGTH:
            commit_id = commit_id[:COMMIT_ID_LENGTH]

        return commit_id

    @property
    def digest(self) -> str:
        """
        Returns the OCI image manifest digest.

        :return: (str) OCI image manifest digest
        :since:  0.7.0
        """

        digest = sha256(self.json).hexdigest()
        return f"sha256:{digest}"

    @property
    def extended_dict(self) -> Dict[str, Any]:
        """
        Returns the final parsed and extended OCI manifest dictionary

        :return: (dict) OCI manifest dictionary
        :since:  1.0.0
        """

        self._ensure_annotations_dict()

        manifest_dict = self.copy()
        manifest_annotations = manifest_dict["annotations"]

        annotation_commit_key = self.__class__.ANNOTATION_COMMIT_KEY
        annotation_version_key = self.__class__.ANNOTATION_VERSION_KEY

        if annotation_commit_key in manifest_annotations:
            manifest_annotations[Manifest.ANNOTATION_COMMIT_DEPRECATED_KEY] = (
                manifest_annotations[annotation_commit_key]
            )

        if annotation_version_key in manifest_annotations:
            manifest_annotations[Manifest.ANNOTATION_VERSION_DEPRECATED_KEY] = (
                manifest_annotations[annotation_version_key]
            )

        return manifest_dict

    @property
    def json(self) -> bytes:
        """
        Returns the OCI image manifest as a JSON

        :return: (bytes) OCI image manifest as JSON
        :since:  0.7.0
        """

        return json.dumps(self.extended_dict).encode("utf-8")

    @property
    def size(self) -> int:
        """
        Returns the OCI image manifest JSON size in bytes.

        :return: (int) OCI image manifest JSON size in bytes
        :since:  0.7.0
        """

        return len(self.json)

    @property
    def version(self) -> str:
        """
        Returns the GardenLinux version of the OCI image manifest.

        :return: (str) OCI image GardenLinux version
        :since:  0.7.0
        """

        annotation_version_key = self.__class__.ANNOTATION_VERSION_KEY

        if annotation_version_key not in self.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected manifest with missing config annotation '{annotation_version_key}' found"
            )

        return self["annotations"][annotation_version_key]  # type: ignore[no-any-return]

    @version.setter
    def version(self, value: str) -> None:
        """
        Sets the GardenLinux version of the OCI image manifest.

        :param value: OCI image GardenLinux version

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"][self.__class__.ANNOTATION_VERSION_KEY] = value

    def _ensure_annotations_dict(self) -> None:
        """
        Ensure the annotations dictionary is initialized.

        :since: 0.7.0
        """

        if "annotations" not in self:
            self["annotations"] = {}
