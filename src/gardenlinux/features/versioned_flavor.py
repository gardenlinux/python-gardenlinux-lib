# -*- coding: utf-8 -*-

"""
Garden Linux versioned flavor
"""

from typing import Optional, Self

from .flavor import Flavor


class VersionedFlavor(Flavor):
    """
    Class to represent a Garden Linux versioned flavor.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        flavor: str,
        arch: str,
        version: str,
    ):
        """
        Constructor __init__(VersionedFlavor)

        :param cname:       CName to represent
        :param arch:        Architecture
        :param commit_hash: Commit ID or hash
        :param version:     Version

        :since: 1.0.0
        """

        Flavor.__init__(self, flavor, arch)

        self._version = version

    @property
    def version(self) -> str:
        """
        Returns the version.

        :return: (str) Version
        :since:  0.7.0
        """

        return self._version

    @property
    def version_epoch(self) -> Optional[int]:
        """
        Returns the Garden Linux version epoch.

        :return: (str) Garden Linux version epoch
        :since:  1.0.0
        """

        epoch = None

        if self._version is not None and "." in self._version:
            epoch = int(self._version.split(".", 1)[0])

        return epoch

    def __str__(self) -> str:
        """
        Returns the Garden Linux versioned flavor.

        :return: (str) Returns the Garden Linux versioned flavor
        :since:  1.0.0
        """

        flavor = Flavor.__str__(self)
        flavor += f"-{self.version}"

        return flavor

    def _copy_from_instance(self, versioned_flavor: Self) -> None:
        """
        Copies values from a given Garden Linux versioned flavor instance.

        :param cname_object: Garden Linux versioned flavor instance

        :since: 1.0.0
        """

        Flavor._copy_from_instance(self, versioned_flavor)

        self._version = versioned_flavor.version
