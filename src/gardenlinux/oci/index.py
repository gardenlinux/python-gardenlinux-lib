# -*- coding: utf-8 -*-

"""
OCI image index
"""

import json
from copy import deepcopy
from typing import Any, Dict

from .image_manifest import ImageManifest
from .manifest import Manifest
from .platform import new_platform
from .schemas import empty_index


class Index(dict):  # type: ignore[type-arg]
    """
    OCI image index

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Constructor __init__(Index)

        :since: 0.7.0
        """

        dict.__init__(self)

        self.update(deepcopy(empty_index))
        self.update(*args)
        self.update(**kwargs)

    @property
    def extended_dict(self) -> Dict[str, Any]:
        """
        Returns the final parsed and extended OCI image index dictionary

        :return: (dict) OCI image index dictionary
        :since:  1.0.0
        """

        return self.copy()

    @property
    def json(self) -> bytes:
        """
        Returns the OCI image index as a JSON

        :return: (bytes) OCI image index as JSON
        :since:  0.7.0
        """

        return json.dumps(self.extended_dict).encode("utf-8")

    @property
    def manifests_as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the OCI image manifests of the index

        :return: (dict) OCI image manifests with CNAME or digest as key
        :since:  0.7.0
        """

        manifests = {}

        for manifest in self["manifests"]:
            if ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY not in manifest.get(
                "annotations", {}
            ):
                manifest_key = ImageManifest(manifest).digest
            else:
                manifest_key = manifest["annotations"][
                    ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY
                ]

            manifests[manifest_key] = manifest

        return manifests

    def add_manifest(self, manifest: Dict[str, Any]) -> None:
        """
        Appends the given OCI image manifest to the index

        :param manifest: OCI image manifest

        :since: 0.7.0
        """

        if not isinstance(manifest, dict):
            raise TypeError("Unexpected manifest type given")

        image_manifest = ImageManifest(manifest)

        if image_manifest.size < 1:
            raise ValueError("Manifest to be added is empty")

        if ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY in manifest.get(
            "annotations", {}
        ):
            image_abn = manifest["annotations"][
                ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY
            ]

            manifests = []

            for existing_manifest in self["manifests"]:
                if image_abn != existing_manifest.get("annotations", {}).get(
                    ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY
                ):
                    manifests.append(existing_manifest)
        else:
            manifests = self["manifests"]

        image_manifest_data = image_manifest.extended_dict

        image_annotations = image_manifest_data["annotations"]

        index_manifest = Manifest()
        index_manifest["mediaType"] = image_manifest_data["mediaType"]
        index_manifest["digest"] = image_manifest.digest
        index_manifest["size"] = image_manifest.size
        index_manifest["annotations"] = image_annotations

        annotation_arch_key = ImageManifest.ANNOTATION_ARCH_KEY
        annotation_os_id_key = ImageManifest.ANNOTATION_OS_ID_KEY
        annotation_version_key = ImageManifest.ANNOTATION_VERSION_KEY

        if (
            annotation_arch_key in image_annotations
            or annotation_os_id_key in image_annotations
            or annotation_version_key in image_annotations
        ):
            kwargs = {}

            annotation_os_id_key = ImageManifest.ANNOTATION_OS_ID_KEY

            if annotation_os_id_key in image_annotations:
                kwargs["os_name"] = image_annotations[annotation_os_id_key]

            annotation_version_key = ImageManifest.ANNOTATION_VERSION_KEY

            if annotation_version_key in image_annotations:
                kwargs["os_version"] = image_annotations[annotation_version_key]

            annotation_arch_key = ImageManifest.ANNOTATION_ARCH_KEY

            if annotation_arch_key in image_annotations:
                kwargs["architecture"] = image_annotations[annotation_arch_key]

            index_manifest["platform"] = new_platform(**kwargs)

        manifests.append(index_manifest)
        self["manifests"] = manifests
