# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Any, Dict

from .schemas import EmptyPlatform


def NewPlatform(architecture: str, version: str) -> Dict[str, Any]:
    platform = deepcopy(EmptyPlatform)
    platform["architecture"] = architecture
    platform["os.version"] = version

    return platform
