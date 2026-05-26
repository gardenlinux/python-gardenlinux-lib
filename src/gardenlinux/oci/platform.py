# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Any, Dict

from .schemas import empty_platform


def new_platform(architecture: str, version: str) -> Dict[str, Any]:
    """
    Create an OCI image platform for the architecture and version given.

    :param architecture: OCI image architecture
    :param manifest_file_path_name: OCI image version

    :return: (object) OCI image platform
    :since:  1.0.0
    """

    platform = deepcopy(empty_platform)
    platform["architecture"] = architecture
    platform["os.version"] = version

    return platform
