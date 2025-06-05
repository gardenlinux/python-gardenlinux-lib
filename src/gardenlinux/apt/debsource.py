# -*- coding: utf-8 -*-

"""
deb sources
"""

import re
from typing import TextIO


class Debsrc:
    """
    Class to reflect deb sources.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: apt
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, deb_source, deb_version):
        """
        Constructor __init__(Debsrc)

        :param deb_source:  Source name
        :param deb_version: Source version

        :since: 0.7.0
        """

        self.deb_source: str = deb_source
        self.deb_version: str = deb_version

    def __repr__(self) -> str:
        """
        python.org: Called by the repr() built-in function to compute the "official" string representation of an object.

        :return: (str) String representation
        :since:  0.7.0
        """

        return f"{self.deb_source} {self.deb_version}"


class DebsrcFile(dict[str, Debsrc]):
    """
    Class to represent deb sources loaded and parsed as dict.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: apt
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    __re = re.compile(
        r"""
        ^(?:
            Package:\s*(?P<source>[a-z0-9.-]+)
            |
            Version:\s*(?P<version>[A-Za-z0-9.+~:-]+)
            |
            Extra-Source-Only:\s*(?P<eso>yes)
            |
            (?P<eoe>)
            |
            # All other fields
            [A-Za-z0-9-]+:.*
            |
            # Continuation field
            \s+.*
        )$
    """,
        re.VERBOSE,
    )

    def read(self, f: TextIO) -> None:
        """
        Read and parse the given TextIO data to extract deb sources.

        :param f: TextIO data to parse

        :since: 0.7.0
        """

        current_source = current_version = None

        for line in f.readlines():
            if match := self.__re.match(line):
                if i := match["source"]:
                    current_source = i
                elif i := match["version"]:
                    current_version = i
                elif match["eso"]:
                    current_source = current_version = None
                elif match["eoe"] is not None:
                    finish()
                    current_source = current_version = None
            else:
                raise RuntimeError(f"Unable to read line: {line}")

        if current_source and current_version:
            self._set_source(current_source, current_version)

    def _set_source(self, source: str, version: str) -> None:
        """
        Sets the dict value based on the given source key.

        :since: 0.7.0
        """

        self[source] = Debsrc(
            deb_source=source,
            deb_version=version,
        )
