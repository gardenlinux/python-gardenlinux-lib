# -*- coding: utf-8 -*-

"""
diff-files comparator generating the list of files for reproducibility test workflow
"""

import filecmp
import importlib
import importlib.resources
import json
import re
from os import PathLike
from pathlib import Path

from ...constants import (
    PODMAN_FS_CHANGE_ADDED,
    PODMAN_FS_CHANGE_DELETED,
    PODMAN_FS_CHANGE_MODIFIED,
)
from ...oci import Image, Podman, PodmanContext


class Comparator(object):
    """
    This class takes either two .tar or two .oci files and identifies differences in the filesystems

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, nightly: bool = False, whitelist: list[str] = []):
        """
        Constructor __init__(Comparator)

        :param nightly:                 Flag indicating if the nightlywhitelist should be used
        :param whitelst:                Additional whitelist

        :since: 1.0.0
        """

        self.whitelist = whitelist

        if nightly:
            self.whitelist += json.loads(
                importlib.resources.read_text(__name__, "nightly_whitelist.json")
            )

    @PodmanContext.wrap
    def generate(
        self, a: PathLike[str], b: PathLike[str], podman: PodmanContext
    ) -> tuple[list[str], bool]:
        """
        Compare two .tar/.oci images with each other

        :param a:                       First .tar/.oci file
        :param b:                       Second .tar/.oci file

        :return: list[Path], bool       Filtered list of paths with different content and flag indicating if whitelist was applied
        :since: 1.0.0
        """

        if filecmp.cmp(a, b, shallow=False):
            return [], False

        a = Path(a)
        a_image_id = None

        b = Path(b)
        b_image_id = None

        differences = []
        podman_api = Podman()

        try:
            if a.suffix == ".oci":
                a_image_id = podman_api.load_oci_archive(a, podman=podman)
            elif a.suffix == ".tar":
                a_image_id = Image.import_plain_tar(a, podman=podman)
            else:
                raise RuntimeError(f"Unsupported file type for comparison: {a.name}")

            if b.suffix == ".oci":
                b_image_id = podman_api.load_oci_archive(b, podman=podman)
            elif b.suffix == ".tar":
                b_image_id = Image.import_plain_tar(b, podman=podman)
            else:
                raise RuntimeError(f"Unsupported file type for comparison: {b.name}")

            image = podman_api.get_image(a_image_id, podman=podman)

            result = image.get_filesystem_changes(
                parent_layer_image_id=b_image_id, podman=podman
            )

            differences = (
                result[PODMAN_FS_CHANGE_ADDED] + result[PODMAN_FS_CHANGE_DELETED]
            )

            whitelist = False

            for entry in result[PODMAN_FS_CHANGE_MODIFIED]:
                if not any(re.match(pattern, entry) for pattern in self.whitelist):
                    differences.append(entry)
                else:
                    whitelist = True
        finally:
            if a_image_id is not None:
                podman.images.remove(a_image_id)
            if b_image_id is not None:
                podman.images.remove(b_image_id)

        return differences, whitelist
