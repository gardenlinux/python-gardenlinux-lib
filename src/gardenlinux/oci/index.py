# -*- coding: utf-8 -*-

import json
from copy import deepcopy

from .schemas import EmptyIndex


class Index(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)

        self.update(deepcopy(EmptyIndex))
        self.update(*args)
        self.update(**kwargs)

    @property
    def json(self):
        return json.dumps(self).encode("utf-8")

    @property
    def manifests_as_dict(self):
        manifests = {}

        for manifest in self["manifests"]:
            if "cname" not in manifest.get("annotations", {}):
                raise RuntimeError(
                    "Unexpected manifest with missing annotation 'cname' found"
                )

            manifests[manifest["annotations"]["cname"]] = manifest

        return manifests

    def append_manifest(self, manifest):
        if not isinstance(manifest, dict):
            raise RuntimeError("Unexpected manifest type given")

        if "cname" not in manifest.get("annotations", {}):
            raise RuntimeError("Unexpected layer with missing annotation 'cname' found")

        cname = manifest["annotations"]["cname"]
        existing_manifest_index = 0

        for existing_manifest in self["manifests"]:
            if "cname" not in existing_manifest.get("annotations", {}):
                raise RuntimeError(
                    "Unexpected layer with missing annotation 'cname' found"
                )

            if cname == existing_manifest["annotations"]["cname"]:
                break

            existing_manifest_index += 1

        if len(self["manifests"]) > existing_manifest_index:
            self["manifests"].pop(existing_manifest_index)

        self["manifests"].append(manifest)
