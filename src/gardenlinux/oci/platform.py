# -*- coding: utf-8 -*-

from copy import deepcopy

from .schemas import EmptyPlatform


def NewPlatform(architecture: str, version: str) -> dict:
    platform = deepcopy(EmptyPlatform)
    platform["architecture"] = architecture
    platform["os.version"] = version

    return platform
