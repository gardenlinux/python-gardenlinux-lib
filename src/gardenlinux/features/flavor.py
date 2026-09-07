# -*- coding: utf-8 -*-

"""
Garden Linux flavor
"""

from typing import Self

from .c_name import CName


class Flavor(CName):
    """
    Class to represent a Garden Linux flavor.

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
        cname: str,
        arch: str,
    ):
        """
        Constructor __init__(Flavor)

        :param cname: CName to represent
        :param arch:  Architecture if not part of cname

        :since: 1.0.0
        """

        CName.__init__(self, cname)
        self._arch = arch

    @property
    def arch(self) -> str:
        """
        Returns the architecture for the CName parsed.

        :return: (str) CName architecture
        :since:  0.7.0
        """

        return self._arch

    @property
    def flavor(self) -> str:
        """
        Returns the Garden Linux flavor parsed.

        :return: (str) Flavor
        :since:  0.7.0
        """

        flavor = CName.__str__(self)
        flavor += f"-{self.arch}"

        return flavor

    def __str__(self) -> str:
        """
        Returns the Garden Linux flavor.

        :return: (str) Flavor
        :since:  1.0.0
        """

        return self.flavor

    def _copy_from_instance(self, flavor: Self) -> None:
        """
        Copies values from a given Garden Linux flavor instance.

        :param cname_object: Flavor instance

        :since: 1.0.0
        """

        CName._copy_from_instance(self, flavor)

        self._arch = flavor.arch
