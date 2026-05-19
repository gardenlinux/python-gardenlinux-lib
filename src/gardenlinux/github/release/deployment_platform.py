import json
from collections.abc import MutableMapping, MutableSequence
from copy import copy
from importlib.resources import files as resource_files
from logging import Logger
from typing import Any, Dict, Optional


class _PermissiveDict(dict[str, Any]):
    """
    "PermissiveDict" implements a dictionary returning empty strings for
    non-existant keys.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                    Apache License, Version 2.0
    """

    def __missing__(self, key: str) -> str:
        """
        python.org: Called by dict.__getitem__() to implement self[key] for dict subclasses when key is not in the dictionary.

        :return: (mixed) Value
        :since:  1.0.0
        """

        return ""


class DeploymentPlatform(object):
    """
    "DeploymentPlatform" represents a Garden Linux release target platform.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    _cached_platforms: Optional[Dict[str, Dict[str, Any]]] = None

    def __init__(self, image_metadata: Dict[str, Any], logger: Optional[Logger] = None):
        self._image_metadata = image_metadata

        assert self.__class__._cached_platforms is not None

        if image_metadata.get("platform") in self.__class__._cached_platforms:
            self._platform_data = self.__class__._cached_platforms[
                image_metadata["platform"]
            ]
        else:
            self._platform_data = self.__class__._cached_platforms["generic"]

        self._logger = logger

    @property
    def artifact_base_name(self) -> str:
        return self._image_metadata["s3_key"].rsplit("/", 1)[1]  # type: ignore[no-any-return]

    @property
    def full_name(self) -> str:
        return self._platform_data["full_name"]  # type: ignore[no-any-return]

    @property
    def image_extension(self) -> str:
        return self._platform_data["image_extension"]  # type: ignore[no-any-return]

    @property
    def published_images_by_deployment(self) -> Dict[str, Any]:
        image_metadata = self._image_metadata.get("published_image_metadata", {})
        result = {}

        match self._platform_data.get("mapping_type"):
            case "azure_gallery_and_marketplace_list":
                entry_template = self._platform_data["mapping_entry_json"][1:-1]
                gallery_images_list = []
                marketplace_images_list = []

                for pset in image_metadata:
                    match pset:
                        case "published_gallery_images":
                            for image_data in image_metadata[pset]:
                                mapping_entry = entry_template.format_map(
                                    _PermissiveDict(image_data)
                                )
                                published_image_data = json.loads(
                                    f"{{{mapping_entry}}}"
                                )

                                gallery_images_list.append(published_image_data)
                        case "published_marketplace_images":
                            for image_data in image_metadata[pset]:
                                mapping_entry = entry_template.format_map(
                                    _PermissiveDict(image_data)
                                )
                                published_image_data = json.loads(
                                    f"{{{mapping_entry}}}"
                                )

                                marketplace_images_list.append(published_image_data)

                if len(gallery_images_list) > 0:
                    result["gallery_images"] = gallery_images_list

                if len(marketplace_images_list) > 0:
                    result["marketplace_images"] = marketplace_images_list
            case "metadata_root":
                entry_template = self._platform_data["mapping_entry_json"][1:-1]

                mapping_entry = entry_template.format_map(
                    _PermissiveDict(image_metadata)
                )
                result["details"] = json.loads(f"{{{mapping_entry}}}")
            case "regions_list":
                regions = []

                for region_set in image_metadata:
                    for image_data in image_metadata[region_set]:
                        entry_template = self._platform_data["mapping_entry_json"][1:-1]

                        mapping_entry = entry_template.format_map(
                            _PermissiveDict(image_data)
                        )
                        regions.append(json.loads(f"{{{mapping_entry}}}"))

                result["regions"] = regions

        return DeploymentPlatform._remove_empty_mapping_values(result)  # type: ignore[no-any-return]

    @property
    def published_images_mapping_type(self) -> str:
        return self._platform_data.get("mapping_type", "undefined")  # type: ignore[no-any-return]

    @property
    def short_name(self) -> str:
        return self._platform_data["short_name"]  # type: ignore[no-any-return]

    def generate_s3_image_url_for_bucket(self, s3_bucket_name: str) -> str:
        s3_url = f"https://{s3_bucket_name}.s3.amazonaws.com/objects/{self.artifact_base_name}/{self.artifact_base_name}.{self.image_extension}"
        return s3_url

    @classmethod
    def new_instance(cls, image_metadata: Dict[str, Any]) -> "DeploymentPlatform":
        if cls._cached_platforms is None:
            cls._cached_platforms = {}

            for resource_file in resource_files(cls.__module__).iterdir():
                if resource_file.is_file() and resource_file.name.endswith(
                    ".platform.json"
                ):
                    platform_data = json.loads(resource_file.read_text())

                    if platform_data.get("short_name") is None:
                        continue

                    cls._cached_platforms[platform_data["short_name"]] = platform_data

        return DeploymentPlatform(image_metadata)

    @staticmethod
    def _remove_empty_mapping_values(mapping_data: Any) -> Any:
        if not isinstance(mapping_data, MutableMapping):
            return mapping_data

        result_mapping = copy(mapping_data)

        for entry_key in mapping_data:
            if (
                isinstance(result_mapping[entry_key], str)
                and result_mapping[entry_key] == ""
            ):
                del result_mapping[entry_key]
            elif isinstance(result_mapping[entry_key], MutableMapping):
                result_mapping[entry_key] = (
                    DeploymentPlatform._remove_empty_mapping_values(
                        result_mapping[entry_key]
                    )
                )
            elif isinstance(result_mapping[entry_key], MutableSequence):
                result_list = []

                for entry in result_mapping[entry_key]:
                    result_list.append(
                        DeploymentPlatform._remove_empty_mapping_values(entry)
                    )

                result_mapping[entry_key] = result_list

        return result_mapping
