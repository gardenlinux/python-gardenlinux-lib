# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Any, Dict

from .schemas import empty_platform


def new_platform(
    os_name: str = "", os_version: str = "", architecture: str = ""
) -> Dict[str, Any]:
    """
    Create an OCI image platform for the architecture and version given.

    :param architecture: OCI image architecture
    :param manifest_file_path_name: OCI image version

    :return: (object) OCI image platform
    :since:  1.0.0
    """

    platform = deepcopy(empty_platform)

    if architecture:
        platform["architecture"] = architecture

    if os_name:
        platform["os"] = os_name

    if os_version:
        platform["os.version"] = os_version

    return platform
