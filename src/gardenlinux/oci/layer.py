# -*- coding: utf-8 -*-

from collections.abc import Mapping
from os import PathLike
from oras.defaults import annotation_title as ANNOTATION_TITLE
from oras.oci import Layer as _Layer
from pathlib import Path
from typing import Optional

from ..constants import GL_MEDIA_TYPE_LOOKUP, GL_MEDIA_TYPES

_SUPPORTED_MAPPING_KEYS = ("annotations",)


class Layer(_Layer, Mapping):
    def __init__(
        self,
        blob_path: PathLike | str,
        media_type: Optional[str] = None,
        is_dir: bool = False,
    ):
        if not isinstance(blob_path, PathLike):
            blob_path = Path(blob_path)

        _Layer.__init__(self, blob_path, media_type, is_dir)

        self._annotations = {
            ANNOTATION_TITLE: blob_path.name,
        }

    def __delitem__(self, key):
        """
        python.org: Called to implement deletion of self[key].

        :param key: Mapping key
        """

        if key == "annotations":
            self._annotations.clear()

        raise KeyError(
            f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
        )

    def __getitem__(self, key):
        """
        python.org: Called to implement evaluation of self[key].

        :param key: Mapping key

        :return: (mixed) Mapping key value
        """

        if key == "annotations":
            return self._annotations

        raise KeyError(
            f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
        )

    def __iter__(self):
        """
        python.org: Return an iterator object.

        :return: (object) Iterator object
        """

        iter(_SUPPORTED_MAPPING_KEYS)

    def __len__(self):
        """
        python.org: Called to implement the built-in function len().

        :return: (int) Number of database instance attributes
        """

        return len(_SUPPORTED_MAPPING_KEYS)

    def __setitem__(self, key, value):
        """
        python.org: Called to implement assignment to self[key].

        :param key: Mapping key
        :param value: self[key] value
        """

        if key == "annotations":
            self._annotations = value

        raise KeyError(
            f"'{self.__class__.__name__}' object is not subscriptable except for keys: {_SUPPORTED_MAPPING_KEYS}"
        )

    def to_dict(self):
        """
        Return a dictionary representation of the layer
        """
        layer = _Layer.to_dict(self)
        layer["annotations"] = self._annotations

        return layer

    @staticmethod
    def generate_metadata_from_file_name(file_name: PathLike | str, arch: str) -> dict:
        """
        :param str file_name: file_name of the blob
        :param str arch: the arch of the target image
        :return: dict of oci layer metadata for a given layer file
        """

        if not isinstance(file_name, PathLike):
            file_name = Path(file_name)

        media_type = Layer.lookup_media_type_for_file_name(file_name)

        return {
            "file_name": file_name.name,
            "media_type": media_type,
            "annotations": {"io.gardenlinux.image.layer.architecture": arch},
        }

    @staticmethod
    def lookup_media_type_for_file_name(file_name: str) -> str:
        """
        :param str file_name: file_name of the target layer
        :return: mediatype
        """

        if not isinstance(file_name, PathLike):
            file_name = Path(file_name)

        for suffix in GL_MEDIA_TYPES:
            if file_name.match(f"*.{suffix}"):
                return GL_MEDIA_TYPE_LOOKUP[suffix]

        raise ValueError(
            f"Media type for {file_name} is not defined. You may want to add the definition to parse_features_lib"
        )
