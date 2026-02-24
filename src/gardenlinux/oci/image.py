# -*- coding: utf-8 -*-

"""
OCI podman
"""

import logging
from os import PathLike
from pathlib import Path
from tarfile import open as tarfile_open
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from podman.domain.images import Image as _Image

from ..constants import (
    PODMAN_FS_CHANGE_ADDED,
    PODMAN_FS_CHANGE_DELETED,
    PODMAN_FS_CHANGE_MODIFIED,
    PODMAN_FS_CHANGE_UNSUPPORTED,
)
from .podman_context import PodmanContext
from .podman_object_context import PodmanObjectContext

PODMAN_CHANGES_KINDS = {
    0: PODMAN_FS_CHANGE_MODIFIED,
    1: PODMAN_FS_CHANGE_ADDED,
    2: PODMAN_FS_CHANGE_DELETED,
}


class Image(PodmanObjectContext):
    """
    Podman image class with extended API features support.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, image: _Image, logger: Optional[logging.Logger] = None):
        """
        Constructor __init__(Image)

        :since: 1.0.0
        """

        PodmanObjectContext.__init__(self, logger)
        self._image_id = image.id

    @property
    def id(self) -> str:
        """
        podman-py.readthedocs.io: Returns the identifier for the object.

        :return: (str) Identifier for the object
        :since:  1.0.0
        """

        return self._image_id  # type: ignore[no-any-return]

    @property
    @PodmanContext.wrap
    def labels(self, podman: PodmanContext) -> Dict[str, str]:
        """
        podman-py.readthedocs.io: Returns the identifier for the object.

        :return: (str) Identifier for the object
        :since:  1.0.0
        """

        return self._get(podman=podman).labels  # type: ignore[no-any-return]

    @property
    @PodmanContext.wrap
    def layer_image_ids(self, podman: PodmanContext) -> List[str]:
        """
        Returns the podman image IDs of all parent layers.

        :param podman: Podman context

        :return: (list) Podman layer image IDs
        :since:  1.0.0
        """

        return [
            image_data["Id"]
            for image_data in self.history(podman=podman)
            if len(image_data["Id"]) == 64
        ]

    def __getattr__(
        self,
        name: str,
    ) -> Any:
        """
        python.org: Called when an attribute lookup has not found the attribute in
        the usual places (i.e. it is not an instance attribute nor is it found in the
        class tree for self).

        :param name: Attribute name

        :return: (mixed) Attribute
        :since:  1.0.0
        """

        @PodmanObjectContext.wrap
        def wrapped_context(podman: PodmanContext, *args: Any, **kwargs: Any) -> Any:
            """
            Wrapping function to use the podman context.
            """

            py_attr = getattr(self._get(podman=podman), name)
            return py_attr(*args, **kwargs)

        return wrapped_context

    def _get(self, podman: PodmanContext) -> _Image:
        """
        Returns the underlying podman image object.

        :param podman: Podman context

        :return: (podman.domains.images.Image) Podman image object
        :since:  1.0.0
        """

        return podman.images.get(self._image_id)

    @PodmanContext.wrap
    def get_filesystem_changes(
        self, podman: PodmanContext, parent_layer_image_id: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Returns the underlying podman image object.

        :param podman: Podman context

        :return: (_Image) Podman image object
        :since:  1.0.0
        """

        changes: Dict[str, List[str]] = {
            PODMAN_FS_CHANGE_ADDED: [],
            PODMAN_FS_CHANGE_DELETED: [],
            PODMAN_FS_CHANGE_MODIFIED: [],
            PODMAN_FS_CHANGE_UNSUPPORTED: [],
        }

        query = ""

        if parent_layer_image_id is not None:
            query = urlencode({"parent": parent_layer_image_id})

        resp = self._raw_request(
            "get", f"/images/{self._image_id}/changes?{query}", podman=podman
        )

        resp.raise_for_status()

        for entry in resp.json():
            changes[
                PODMAN_CHANGES_KINDS.get(entry["Kind"], PODMAN_FS_CHANGE_UNSUPPORTED)
            ].append(entry["Path"])

        return changes

    @staticmethod
    @PodmanContext.wrap
    def import_plain_tar(tar_file_name: PathLike[str], podman: PodmanContext) -> str:
        """
        Import a plain filesystem tar archive into an OCI image.

        :param tar_file_name: Plain filesystem tar archive
        :param podman: Podman context

        :return: (str) Podman image ID
        :since:  1.0.0
        """

        image_id = None

        with TemporaryDirectory() as tmpdir:
            container_file_name = Path(tmpdir, "ContainerFile")
            tarfile_open(tar_file_name, dereference=True).extractall(
                path=Path(tmpdir, "archive_content"),
                filter="fully_trusted",
                numeric_owner=True,
            )

            with container_file_name.open("w") as container_file:
                container_file.write("FROM scratch\nCOPY archive_content/ /")

            image, _ = podman.images.build(path=tmpdir, dockerfile=container_file_name)
            image_id = image.id

        return image_id  # type: ignore[no-any-return]
