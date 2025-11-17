# -*- coding: utf-8 -*-

from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from oras.defaults import annotation_title as ANNOTATION_TITLE
from oras.oci import Layer as _Layer

from ..constants import GL_MEDIA_TYPE_LOOKUP, GL_MEDIA_TYPES

_SUPPORTED_MAPPING_KEYS = ("annotations",)


class Layer(_Layer, Mapping):  # type: ignore[misc, type-arg]
    """
    OCI image layer

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        blob_path: PathLike[str] | str,
        media_type: Optional[str] = None,
        is_dir: bool = False,
    ):
        """
        Constructor __init__(Index)

        :param blob_path: The path of the blob for the layer
        :param media_type: Media type for the blob (optional)
        :param is_dir: Is the blob a directory?

        :since: 0.7.0
        """

        if not isinstance(blob_path, PathLike):
            blob_path = Path(blob_path)

        _Layer.__init__(self, blob_path, media_type, is_dir)

        self._annotations = {
            ANNOTATION_TITLE: blob_path.name,  # type: ignore[attr-defined]
        }

    @property
    def dict(self) -> Dict[Any, Any]:
        """
        Return a dictionary representation of the layer

        :return: (dict) OCI manifest layer metadata dictionary
        :since:  0.7.2
        """

        layer = _Layer.to_dict(self)
        layer["annotations"] = self._annotations

        return layer  # type: ignore[no-any-return]

    def __delitem__(self, key: str) -> None:
        """
        python.org: Called to implement deletion of self[key].

        :param key: Mapping key

        :since: 0.7.0
        """

        if key == "annotations":
            self._annotations.clear()
        else:
            raise KeyError(
                f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
            )

    def __getitem__(self, key: str) -> Any:
        """
        python.org: Called to implement evaluation of self[key].

        :param key: Mapping key

        :return: (mixed) Mapping key value
        :since:  0.7.0
        """

        if key == "annotations":
            return self._annotations

        raise KeyError(
            f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
        )

    def __iter__(self) -> Iterator[str]:
        """
        python.org: Return an iterator object.

        :return: (object) Iterator object
        :since:  0.7.0
        """

        return iter(_SUPPORTED_MAPPING_KEYS)

    def __len__(self) -> int:
        """
        python.org: Called to implement the built-in function len().

        :return: (int) Number of attributes
        :since:  0.7.0
        """

        return len(_SUPPORTED_MAPPING_KEYS)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        python.org: Called to implement assignment to self[key].

        :param key: Mapping key
        :param value: self[key] value

        :since: 0.7.0
        """

        if key == "annotations":
            self._annotations = value
        else:
            raise KeyError(
                f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
            )

    @staticmethod
    def generate_metadata_from_file_name(
        file_name: PathLike[str] | str, arch: str
    ) -> Dict[str, Any]:
        """
        Generates OCI manifest layer metadata for the given file path and name.

        :param file_name: File path and name of the target layer
        :param arch: The arch of the target image

        :return: (dict) OCI manifest layer metadata dictionary
        :since:  0.7.0
        """

        if not isinstance(file_name, PathLike):
            file_name = Path(file_name)

        media_type = Layer.lookup_media_type_for_file_name(file_name)

        return {
            "file_name": file_name.name,  # type: ignore[attr-defined]
            "media_type": media_type,
            "annotations": {"io.gardenlinux.image.layer.architecture": arch},
        }

    @staticmethod
    def lookup_media_type_for_file_name(file_name: PathLike[str] | str) -> str:
        """
        Looks up the media type based on file name or extension.

        :param file_name: File path and name of the target layer

        :return: (str) Media type
        :since:  0.7.0
        """

        if not isinstance(file_name, PathLike):
            file_name = Path(file_name)

        for lookup_name in GL_MEDIA_TYPES:
            if file_name.match(f"*.{lookup_name}") or file_name.name == lookup_name:  # type: ignore[attr-defined]
                return GL_MEDIA_TYPE_LOOKUP[lookup_name]

        raise ValueError(
            f"Media type for {file_name} is not defined. You may want to add the definition to parse_features_lib"
        )
