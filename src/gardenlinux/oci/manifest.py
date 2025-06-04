# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from hashlib import sha256
from oras.defaults import unknown_config_media_type as UNKNOWN_CONFIG_MEDIA_TYPE
from oras.oci import EmptyManifest, Layer
from os import PathLike
from pathlib import Path

from ..features import CName

from .platform import NewPlatform
from .schemas import EmptyManifestMetadata


class Manifest(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)

        self._config_bytes = b"{}"

        self.update(deepcopy(EmptyManifest))
        self.update(*args)
        self.update(**kwargs)

    @property
    def arch(self):
        if "architecture" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'architecture' found"
            )

        return self["annotations"]["architecture"]

    @arch.setter
    def arch(self, value):
        self._ensure_annotations_dict()
        self["annotations"]["architecture"] = value

    @property
    def cname(self):
        if "cname" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'cname' found"
            )

        return self["annotations"]["cname"]

    @cname.setter
    def cname(self, value):
        self._ensure_annotations_dict()
        self["annotations"]["cname"] = value

    @property
    def commit(self):
        if "commit" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'commit' found"
            )

        return self["annotations"]["commit"]

    @commit.setter
    def commit(self, value):
        self._ensure_annotations_dict()
        self["annotations"]["commit"] = value

    @property
    def config_json(self):
        return self._config_bytes

    @property
    def digest(self):
        digest = sha256(self.json).hexdigest()
        return f"sha256:{digest}"

    @property
    def feature_set(self):
        if "feature_set" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'feature_set' found"
            )

        return self["annotations"]["feature_set"]

    @feature_set.setter
    def feature_set(self, value):
        self._ensure_annotations_dict()
        self["annotations"]["feature_set"] = value

    @property
    def flavor(self):
        return CName(self.cname).flavor

    @property
    def json(self):
        return json.dumps(self).encode("utf-8")

    @property
    def layers_as_dict(self):
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
        return len(self.json)

    @property
    def version(self):
        if "version" not in self.get("annotations", {}):
            raise RuntimeError(
                "Unexpected manifest with missing config annotation 'version' found"
            )

        return self["annotations"]["version"]

    @version.setter
    def version(self, value):
        self._ensure_annotations_dict()
        self["annotations"]["version"] = value

    def config_from_dict(self, config: dict, annotations: dict):
        """
        Write a new OCI configuration to file, and generate oci metadata for it
        For reference see https://github.com/opencontainers/image-spec/blob/main/config.md
        annotations, mediatype, size, digest are not part of digest and size calculation,
        and therefore must be attached to the output dict and not written to the file.

        :param config: dict with custom configuration (the payload of the configuration)
        :param annotations: dict with custom annotations to be attached to metadata part of config

        """

        self._config_bytes = json.dumps(config).encode("utf-8")

        config["annotations"] = annotations
        config["mediaType"] = UNKNOWN_CONFIG_MEDIA_TYPE
        config["size"] = len(self._config_bytes)
        config["digest"] = f"sha256:{sha256(self._config_bytes).hexdigest()}"

        self["config"] = config

    def append_layer(self, layer):
        if not isinstance(layer, Layer):
            raise RuntimeError("Unexpected layer type given")

        layer_dict = layer.to_dict()

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
