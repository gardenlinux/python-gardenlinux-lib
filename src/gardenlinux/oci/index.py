# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from typing import Any, Dict

from .schemas import EmptyIndex


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

        self.update(deepcopy(EmptyIndex))
        self.update(*args)
        self.update(**kwargs)

    @property
    def json(self) -> bytes:
        """
        Returns the OCI image index as a JSON

        :return: (bytes) OCI image index as JSON
        :since:  0.7.0
        """

        return json.dumps(self).encode("utf-8")

    @property
    def manifests_as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the OCI image manifests of the index

        :return: (dict) OCI image manifests with CNAME or digest as key
        :since:  0.7.0
        """

        manifests = {}

        for manifest in self["manifests"]:
            if "annotations" not in manifest or "cname" not in manifest["annotations"]:
                manifest_key = manifest["digest"]
            else:
                manifest_key = manifest["annotations"]["cname"]

            manifests[manifest_key] = manifest

        return manifests

    def append_manifest(self, manifest: Dict[str, Any]) -> None:
        """
        Appends the given OCI image manifest to the index

        :param manifest: OCI image manifest

        :since: 0.7.0
        """

        if not isinstance(manifest, dict):
            raise RuntimeError("Unexpected manifest type given")

        if "cname" not in manifest.get("annotations", {}):
            raise RuntimeError("Unexpected layer with missing annotation 'cname' found")

        cname = manifest["annotations"]["cname"]
        existing_manifest_index = 0

        for existing_manifest in self["manifests"]:
            if "cname" not in existing_manifest.get("annotations", {}):
                existing_manifest_index += 1
                continue

            if cname == existing_manifest["annotations"]["cname"]:
                break

            existing_manifest_index += 1

        if len(self["manifests"]) > existing_manifest_index:
            self["manifests"].pop(existing_manifest_index)

        self["manifests"].append(manifest)
