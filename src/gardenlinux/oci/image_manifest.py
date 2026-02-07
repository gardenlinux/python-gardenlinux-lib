# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import Any, Dict

from oras.defaults import annotation_title as ANNOTATION_TITLE

from ..constants import GL_DISTRIBUTION_NAME, GL_REPOSITORY_URL
from ..features import CName
from .layer import Layer
from .manifest import Manifest
from .platform import NewPlatform
from .schemas import EmptyManifestMetadata


class ImageManifest(Manifest):
    """
    OCI image manifest

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.10.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    ANNOTATION_ARCH_KEY = "org.opencontainers.image.architecture"
    """
    OCI image manifest architecture annotation
    """
    ANNOTATION_CNAME_KEY = "cname"
    """
    OCI image manifest GardenLinux canonical name annotation
    """
    ANNOTATION_DESCRIPTION_KEY = "org.opencontainers.image.description"
    """
    OCI image manifest description annotation
    """
    ANNOTATION_FEATURE_SET_KEY = "feature_set"
    """
    OCI image manifest GardenLinux feature set annotation
    """
    ANNOTATION_SOURCE_REPO_KEY = "org.opencontainers.image.source"
    """
    OCI image manifest GardenLinux source repository URL annotation
    """
    ANNOTATION_TITLE_KEY = ANNOTATION_TITLE
    """
    OCI image manifest title annotation
    """

    @property
    def arch(self) -> str:
        """
        Returns the architecture of the OCI image manifest.

        :return: (str) OCI image architecture
        :since:  0.7.0
        """

        if ImageManifest.ANNOTATION_ARCH_KEY not in self.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected manifest with missing config annotation '{ImageManifest.ANNOTATION_ARCH_KEY}' found"
            )

        return self["annotations"][ImageManifest.ANNOTATION_ARCH_KEY]  # type: ignore[no-any-return]

    @arch.setter
    def arch(self, value: str) -> None:
        """
        Sets the architecture of the OCI image manifest.

        :param value: OCI image architecture

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"][ImageManifest.ANNOTATION_ARCH_KEY] = value

    @property
    def cname(self) -> str:
        """
        Returns the GardenLinux canonical name of the OCI image manifest.

        :return: (str) OCI image GardenLinux canonical name
        :since:  0.7.0
        """

        if ImageManifest.ANNOTATION_CNAME_KEY not in self.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected manifest with missing config annotation '{ImageManifest.ANNOTATION_CNAME_KEY}' found"
            )

        return self["annotations"][ImageManifest.ANNOTATION_CNAME_KEY]  # type: ignore[no-any-return]

    @cname.setter
    def cname(self, value: str) -> None:
        """
        Sets the GardenLinux canonical name of the OCI image manifest.

        :param value: OCI image GardenLinux canonical name

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"][ImageManifest.ANNOTATION_CNAME_KEY] = value

    @property
    def feature_set(self) -> str:
        """
        Returns the GardenLinux feature set of the OCI image manifest.

        :return: (str) OCI image GardenLinux feature set
        :since:  0.7.0
        """

        if ImageManifest.ANNOTATION_FEATURE_SET_KEY not in self.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected manifest with missing config annotation '{ImageManifest.ANNOTATION_FEATURE_SET_KEY}' found"
            )

        return self["annotations"][ImageManifest.ANNOTATION_FEATURE_SET_KEY]  # type: ignore[no-any-return]

    @feature_set.setter
    def feature_set(self, value: str) -> None:
        """
        Sets the GardenLinux feature set of the OCI image manifest.

        :param value: OCI image GardenLinux feature set

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"][ImageManifest.ANNOTATION_FEATURE_SET_KEY] = value

    @property
    def flavor(self) -> str:
        """
        Returns the GardenLinux flavor of the OCI image manifest.

        :return: (str) OCI image GardenLinux flavor
        :since:  0.7.0
        """

        return CName(self.cname).flavor

    @property
    def extended_dict(self) -> Dict[str, Any]:
        """
        Returns the final parsed and extended OCI manifest dictionary

        :return: (dict) OCI manifest dictionary
        :since:  1.0.0
        """

        manifest_dict = Manifest(self).extended_dict
        manifest_annotations = manifest_dict["annotations"]

        if ImageManifest.ANNOTATION_TITLE_KEY not in manifest_annotations:
            manifest_annotations[ImageManifest.ANNOTATION_TITLE_KEY] = (
                GL_DISTRIBUTION_NAME
            )

        manifest_description = manifest_annotations[ImageManifest.ANNOTATION_TITLE_KEY]

        if ImageManifest.ANNOTATION_SOURCE_REPO_KEY not in manifest_annotations:
            manifest_annotations[ImageManifest.ANNOTATION_SOURCE_REPO_KEY] = (
                GL_REPOSITORY_URL
            )

        if ImageManifest.ANNOTATION_ARCH_KEY in manifest_annotations:
            manifest_annotations["architecture"] = self.arch
            manifest_description += f" ({self.arch})"

        if ImageManifest.ANNOTATION_VERSION_KEY in manifest_annotations:
            manifest_annotations["org.opencontainers.image.version"] = self.version
            manifest_description += " " + self.version

        if ImageManifest.ANNOTATION_COMMIT_KEY in manifest_annotations:
            manifest_annotations["org.opencontainers.image.revision"] = self.commit
            manifest_description += f" ({self.commit})"

        if ImageManifest.ANNOTATION_FEATURE_SET_KEY in manifest_annotations:
            manifest_description += (
                " - " + manifest_annotations[ImageManifest.ANNOTATION_FEATURE_SET_KEY]
            )

        if ImageManifest.ANNOTATION_DESCRIPTION_KEY not in manifest_annotations:
            manifest_annotations[ImageManifest.ANNOTATION_DESCRIPTION_KEY] = (
                manifest_description
            )

        return manifest_dict

    @property
    def layers_as_dict(self) -> Dict[str, Any]:
        """
        Returns the OCI image manifest layers as a dictionary.

        :return: (dict) OCI image manifest layers with title as key
        :since:  0.7.0
        """

        layers = {}

        for layer in self["layers"]:
            if ImageManifest.ANNOTATION_TITLE_KEY not in layer.get("annotations", {}):
                raise RuntimeError(
                    f"Unexpected layer with missing annotation '{ImageManifest.ANNOTATION_TITLE_KEY}' found"
                )

            layers[layer["annotations"][ImageManifest.ANNOTATION_TITLE_KEY]] = layer

        return layers

    def append_layer(self, layer: Layer | Dict[str, Any]) -> None:
        """
        Appends the given OCI image manifest layer to the manifest

        :param layer: OCI image manifest layer

        :since: 0.7.0
        """

        if isinstance(layer, Layer):
            layer_dict = layer.dict
        else:
            layer_dict = layer

        if ImageManifest.ANNOTATION_TITLE_KEY not in layer_dict.get("annotations", {}):
            raise RuntimeError(
                f"Unexpected layer with missing annotation '{ImageManifest.ANNOTATION_TITLE_KEY}' found"
            )

        image_title = layer_dict["annotations"][ImageManifest.ANNOTATION_TITLE_KEY]
        existing_layer_index = 0

        for existing_layer in self["layers"]:
            if ImageManifest.ANNOTATION_TITLE_KEY not in existing_layer.get(
                "annotations", {}
            ):
                raise RuntimeError(
                    f"Unexpected layer with missing annotation '{ImageManifest.ANNOTATION_TITLE_KEY}' found"
                )

            if (
                image_title
                == existing_layer["annotations"][ImageManifest.ANNOTATION_TITLE_KEY]
            ):
                break

            existing_layer_index += 1

        if len(self["layers"]) > existing_layer_index:
            self["layers"].pop(existing_layer_index)

        self["layers"].append(layer_dict)

    def write_metadata_file(self, manifest_file_path_name: PathLike[str] | str) -> None:
        """
        Create OCI image manifest metadata and write it to the file given.

        :param manifest_file_path_name: OCI image manifest metadata file

        :since: 0.7.0
        """

        if not isinstance(manifest_file_path_name, PathLike):
            manifest_file_path_name = Path(manifest_file_path_name)

        metadata_annotations = {
            "cname": self.cname,
            "architecture": self.arch,
            "feature_set": self.feature_set,
        }

        metadata = deepcopy(EmptyManifestMetadata)
        metadata["mediaType"] = "application/vnd.oci.image.manifest.v1+json"
        metadata["digest"] = self.digest
        metadata["size"] = self.size
        metadata["annotations"] = metadata_annotations
        metadata["platform"] = NewPlatform(self.arch, self.version)

        with open(manifest_file_path_name, "w") as fp:
            fp.write(json.dumps(metadata))
