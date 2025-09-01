# -*- coding: utf-8 -*-

"""
Canonical name (cname)
"""

import re
from typing import Optional

from ..constants import ARCHS
from .parser import Parser


class CName(object):
    """
    Class to represent a canonical name (cname).

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, cname, arch=None, commit_id=None, version=None):
        """
        Constructor __init__(CName)

        :param cname:     Canonical name to represent
        :param arch:      Architecture if not part of cname
        :param commit_id: Commit ID if not part of cname
        :param version:   Version if not part of cname

        :since: 0.7.0
        """

        self._arch = None
        self._flavor = None
        self._commit_id = None
        self._version = None

        re_match = re.match(
            "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
            cname,
        )

        assert re_match, f"Not a valid GardenLinux canonical name {cname}"

        if re_match.lastindex == 1:
            self._flavor = re_match[1]
        else:
            self._commit_id = re_match[7]
            self._flavor = re_match[1]
            self._version = re_match[6]

            if re_match[4] in ARCHS:
                self._arch = re_match[4]
            else:
                self._flavor += re_match[3]

        if self._arch is None and arch is not None:
            self._arch = arch

        if self._version is None and version is not None:
            # Support version values formatted as <version>-<commit_id>
            if commit_id is None:
                re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", version)
                assert re_match, f"Not a valid version {version}"

                self._commit_id = re_match[3]
                self._version = re_match[1]
            else:
                self._commit_id = commit_id
                self._version = version

    @property
    def arch(self) -> Optional[str]:
        """
        Returns the architecture for the cname parsed.

        :return: (str) CName architecture
        """

        return self._arch

    @property
    def cname(self) -> str:
        """
        Returns the cname parsed.

        :return: (str) CName
        """

        cname = self._flavor

        if self._arch is not None:
            cname += f"-{self._arch}"

        if self._commit_id is not None:
            cname += f"-{self.version_and_commit_id}"

        return cname

    @property
    def commit_id(self) -> Optional[str]:
        """
        Returns the commit ID if part of the cname parsed.

        :return: (str) Commit ID
        """

        return self._commit_id

    @property
    def flavor(self) -> str:
        """
        Returns the flavor for the cname parsed.

        :return: (str) Flavor
        """

        return self._flavor

    @property
    def feature_set(self) -> str:
        """
        Returns the feature set for the cname parsed.

        :return: (str) Feature set of the cname
        """

        return Parser().filter_as_string(self.flavor)

    @property
    def platform(self) -> str:
        """
        Returns the platform for the cname parsed.

        :return: (str) Flavor
        """

        return re.split("[_-]", self._flavor, maxsplit=1)[0]

    @property
    def version(self) -> Optional[str]:
        """
        Returns the version if part of the cname parsed.

        :return: (str) Version
        """

        return self._version

    @property
    def version_and_commit_id(self) -> Optional[str]:
        """
        Returns the version and commit ID if part of the cname parsed.

        :return: (str) Version and commit ID
        """

        if self._commit_id is None:
            return None

        return f"{self._version}-{self._commit_id}"
