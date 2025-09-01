# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from hashlib import sha256
from os import PathLike
from pathlib import Path

from oras.defaults import unknown_config_media_type as UNKNOWN_CONFIG_MEDIA_TYPE
from oras.oci import EmptyManifest, Layer

from ..features import CName
from .platform import NewPlatform
from .schemas import EmptyManifestMetadata


class Manifest(dict):
    """
    OCI image manifest

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor __init__(Manifest)

        :since: 0.7.0
        """

        dict.__init__(self)

        self._config_bytes = b"{}"

        self.update(deepcopy(EmptyManifest))
        self.update(*args)
        self.update(**kwargs)

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
    def commit(self):
        """
        Returns the GardenLinux Git commit ID of the OCI image manifest.

        :return: (str) OCI image GardenLinux Git commit ID
        :since:  0.7.0
        """

        if "commit" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'commit' found"
            )

        return self["annotations"]["commit"]

    @commit.setter
    def commit(self, value):
        """
        Sets the GardenLinux Git commit ID of the OCI image manifest.

        :param value: OCI image GardenLinux Git commit ID

        :since: 0.7.0
        """

        self._ensure_annotations_dict()
        self["annotations"]["commit"] = value

    @property
    def config_json(self):
        """
        Returns the OCI image manifest config.

        :return: (bytes) OCI image manifest config
        :since:  0.7.0
        """

        return self._config_bytes

    @property
    def digest(self):
        """
        Returns the OCI image manifest digest.

        :return: (str) OCI image manifest digest
        :since:  0.7.0
        """

        digest = sha256(self.json).hexdigest()
        return f"sha256:{digest}"

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
    def json(self):
        """
        Returns the OCI image manifest as a JSON

        :return: (bytes) OCI image manifest as JSON
        :since:  0.7.0
        """

        return json.dumps(self).encode("utf-8")

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
    def size(self):
        """
        Returns the OCI image manifest JSON size in bytes.

        :return: (int) OCI image manifest JSON size in bytes
        :since:  0.7.0
        """

        return len(self.json)

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

    def config_from_dict(self, config: dict, annotations: dict):
        """
        Write a new OCI configuration to file, and generate oci metadata for it.

        For reference see https://github.com/opencontainers/image-spec/blob/main/config.md
        annotations, mediatype, size, digest are not part of digest and size calculation,
        and therefore must be attached to the output dict and not written to the file.

        :param config: dict with custom configuration (the payload of the configuration)
        :param annotations: dict with custom annotations to be attached to metadata part of config

        :since: 0.7.0
        """

        self._config_bytes = json.dumps(config).encode("utf-8")

        config["annotations"] = annotations
        config["mediaType"] = UNKNOWN_CONFIG_MEDIA_TYPE
        config["size"] = len(self._config_bytes)
        config["digest"] = f"sha256:{sha256(self._config_bytes).hexdigest()}"

        self["config"] = config

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

    def _ensure_annotations_dict(self):
        if "annotations" not in self:
            self["annotations"] = {}

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
