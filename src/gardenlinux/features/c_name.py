# -*- coding: utf-8 -*-

"""
Garden Linux Canonical Name (CName)
"""

from os import environ
from typing import Any, Dict, List, Optional, Self

from ..constants import GL_PLATFORM_FRANKENSTEIN
from .parser import Parser


class CName(object):
    """
    Class to represent a Garden Linux Canonical Name (CName).

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        cname: str,
    ):
        """
        Constructor __init__(CName)

        :param cname: CName to represent

        :since: 1.0.0
        """

        self._cname = cname
        self._feature_elements_cached: Optional[List[str]] = None
        self._feature_flags_cached: Optional[List[str]] = None
        self._feature_platforms_cached: Optional[List[str]] = None
        self._feature_set_cached: Optional[str] = None
        self._features_cached: Optional[Dict[str, Any]] = None
        self._platform_cached: Optional[str] = None
        self._platform_variant_cached: Optional[str] = None

        self._flag_frankenstein = bool(environ.get("GL_ALLOW_FRANKENSTEIN", False))

        self._flag_multiple_platforms = bool(
            environ.get("GL_ALLOW_MULTIPLE_PLATFORMS", False)
        )

        if self._flag_frankenstein:
            self._flag_multiple_platforms = True

    @property
    def cname(self) -> str:
        """
        Returns the CName parsed.

        :return: (str) CName
        :since:  0.7.0
        """

        return self._cname

    @property
    def features(self) -> Dict[str, Any]:
        """
        Returns the features for the CName parsed.

        :return: (dict) Features of the CName
        :since:  0.10.14
        """

        if self._features_cached is None:
            self._features_cached = Parser().filter_as_dict(self.cname)

        return self._features_cached

    @property
    def feature_set(self) -> str:
        """
        Returns the feature set for the CName parsed.

        :return: (str) Feature set of the CName
        :since:  0.7.0
        """

        if self._feature_set_cached is not None:
            return self._feature_set_cached

        return Parser().filter_as_string(self.cname)

    @property
    def feature_set_element(self) -> str:
        """
        Returns the feature set of type "element" for the CName parsed.

        :return: (str) Feature set elements
        :since:  1.0.0
        """

        if self._feature_elements_cached is not None:
            return ",".join(self._feature_elements_cached)

        return ",".join(self.features["element"])

    @property
    def feature_set_flag(self) -> str:
        """
        Returns the feature set of type "flag" for the CName parsed.

        :return: (str) Feature set flags
        :since:  1.0.0
        """

        if self._feature_flags_cached is not None:
            return ",".join(self._feature_flags_cached)

        return ",".join(self.features["flag"])

    @property
    def feature_set_platform(self) -> str:
        """
        Returns the feature set of type "platform" for the CName parsed.

        :return: (str) Feature set platform
        :since:  1.0.0
        """

        if self._feature_platforms_cached is None:
            platforms = self.features["platform"]
        else:
            platforms = self._feature_platforms_cached

        if self._flag_multiple_platforms:
            return ",".join(platforms)

        assert len(platforms) < 2, "Only one platform is supported"
        return platforms[0]  # type: ignore[no-any-return]

    @property
    def feature_set_list(self) -> List[str]:
        """
        Returns the feature set for the CName parsed.

        :return: (list) Feature set list of the CName
        :since:  0.10.12
        """

        if self._feature_set_cached is not None:
            return self._feature_set_cached.split(",")

        return Parser().filter_as_list(self.cname)

    @property
    def platform(self) -> str:
        """
        Returns the platform for the CName parsed.

        :return: (str) Platform
        :since:  0.7.0
        """

        if self._platform_cached is not None:
            platforms = [self._platform_cached]
        elif self._feature_platforms_cached is not None:
            platforms = self._feature_platforms_cached
        else:
            platforms = self.features["platform"]

        if self._flag_frankenstein and len(platforms) > 1:
            return GL_PLATFORM_FRANKENSTEIN

        if not self._flag_multiple_platforms:
            assert len(platforms) < 2
            "Only one platform is supported"

        return platforms[0]

    @property
    def platform_variant(self) -> Optional[str]:
        """
        Returns the platform variant for the CName parsed.

        :return: (str) Platform variant
        :since:  1.0.0
        """

        if self._platform_variant_cached is not None:
            return self._platform_variant_cached

        # @TODO: Platform variant is set by GardenLinux features to the release file. If not read or cached it is currently invisible for this library.
        return None

    @platform_variant.setter
    def platform_variant(self, variant: str) -> None:
        """
        Sets the the platform variant

        :param variant: Platform variant

        :since: 1.0.0
        """

        self._platform_variant_cached = variant

    def __str__(self) -> str:
        """
        Returns the Garden Linux Canonical Name.

        :return: (str) Returns the Garden Linux Canonical Name
        :since:  1.0.0
        """

        return self.cname

    def _copy_from_instance(self, c_name: Self) -> None:
        """
        Copies values from a given Garden Linux Canonical Name instance.

        :param cname_object: Garden Linux Canonical Name instance

        :since: 1.0.0
        """

        self._cname = c_name.cname
        self._feature_set_cached = c_name.feature_set
        self._feature_elements_cached = c_name.feature_set_element.split(",")
        self._feature_flags_cached = c_name.feature_set_flag.split(",")
        self._feature_platforms_cached = c_name.feature_set_platform.split(",")
        self._platform_cached = c_name.platform
        self._platform_variant_cached = c_name.platform_variant
