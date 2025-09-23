# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from os import PathLike
from pathlib import Path

from oras.oci import Layer

from ..features import CName
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

    @property
    def arch(self):
        """
        Returns the architecture of the OCI image manifest.

        :return: (str) OCI image architecture
        :since:  0.7.0
        """

        if "architecture" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'architecture' found"
            )

        return self["annotations"]["architecture"]

    @arch.setter
    def arch(self, value):
        """
        Sets the architecture of the OCI image manifest.

        :param value: OCI image architecture

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"]["architecture"] = value

    @property
    def cname(self):
        """
        Returns the GardenLinux canonical name of the OCI image manifest.

        :return: (str) OCI image GardenLinux canonical name
        :since:  0.7.0
        """

        if "cname" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'cname' found"
            )

        return self["annotations"]["cname"]

    @cname.setter
    def cname(self, value):
        """
        Sets the GardenLinux canonical name of the OCI image manifest.

        :param value: OCI image GardenLinux canonical name

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"]["cname"] = value

    @property
    def feature_set(self):
        """
        Returns the GardenLinux feature set of the OCI image manifest.

        :return: (str) OCI image GardenLinux feature set
        :since:  0.7.0
        """

        if "feature_set" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'feature_set' found"
            )

        return self["annotations"]["feature_set"]

    @feature_set.setter
    def feature_set(self, value):
        """
        Sets the GardenLinux feature set of the OCI image manifest.

        :param value: OCI image GardenLinux feature set

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"]["feature_set"] = value

    @property
    def flavor(self):
        """
        Returns the GardenLinux flavor of the OCI image manifest.

        :return: (str) OCI image GardenLinux flavor
        :since:  0.7.0
        """

        return CName(self.cname).flavor

    @property
    def layers_as_dict(self):
        """
        Returns the OCI image manifest layers as a dictionary.

        :return: (dict) OCI image manifest layers with title as key
        :since:  0.7.0
        """

        layers = {}

        for layer in self["layers"]:
            if "org.opencontainers.image.title" not in layer.get("annotations", {}):
                raise RuntimeError(
                    "Unexpected layer with missing annotation 'org.opencontainers.image.title' found"
                )

            layers[layer["annotations"]["org.opencontainers.image.title"]] = layer

        return layers

    @property
    def version(self):
        """
        Returns the GardenLinux version of the OCI image manifest.

        :return: (str) OCI image GardenLinux version
        :since:  0.7.0
        """

        if "version" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'version' found"
            )

        return self["annotations"]["version"]

    @version.setter
    def version(self, value):
        """
        Sets the GardenLinux version of the OCI image manifest.

        :param value: OCI image GardenLinux version

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"]["version"] = value

    def append_layer(self, layer):
        """
        Appends the given OCI image manifest layer to the manifest

        :param layer: OCI image manifest layer

        :since: 0.7.0
        """

        if not isinstance(layer, Layer):
            raise RuntimeError("Unexpected layer type given")

        layer_dict = layer.dict

        if "org.opencontainers.image.title" not in layer_dict.get("annotations", {}):
            raise RuntimeError(
                "Unexpected layer with missing annotation 'org.opencontainers.image.title' found"
            )

        image_title = layer_dict["annotations"]["org.opencontainers.image.title"]
        existing_layer_index = 0

        for existing_layer in self["layers"]:
            if "org.opencontainers.image.title" not in existing_layer.get(
                "annotations", {}
            ):
                raise RuntimeError(
                    "Unexpected layer with missing annotation 'org.opencontainers.image.title' found"
                )

            if (
                image_title
                == existing_layer["annotations"]["org.opencontainers.image.title"]
            ):
                break

            existing_layer_index += 1

        if len(self["layers"]) > existing_layer_index:
            self["layers"].pop(existing_layer_index)

        self["layers"].append(layer_dict)

    def write_metadata_file(self, manifest_file_path_name):
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
