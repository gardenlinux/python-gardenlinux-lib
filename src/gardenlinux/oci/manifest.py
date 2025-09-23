# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from hashlib import sha256

from oras.defaults import unknown_config_media_type as UNKNOWN_CONFIG_MEDIA_TYPE
from oras.oci import EmptyManifest


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
    def commit(self):
        """
        Returns the GardenLinux Git commit ID of the OCI manifest.

        :return: (str) OCI GardenLinux Git commit ID
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
        Sets the GardenLinux Git commit ID of the OCI manifest.

        :param value: OCI GardenLinux Git commit ID

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
    def json(self):
        """
        Returns the OCI image manifest as a JSON

        :return: (bytes) OCI image manifest as JSON
        :since:  0.7.0
        """

        return json.dumps(self).encode("utf-8")

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

    def _ensure_annotations_dict(self):
        if "annotations" not in self:
            self["annotations"] = {}
