# -*- coding: utf-8 -*-

from typing import Optional
import re

from ..constants import ARCHS

from .parser import Parser


class CName(object):
    def __init__(self, cname, arch=None, version=None):
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
            re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", version)
            assert re_match, f"Not a valid version {version}"

            self._commit_id = re_match[3]
            self._version = re_match[1]

    @property
    def arch(self) -> Optional[str]:
        return self._arch

    @property
    def cname(self) -> str:
        cname = self._flavor

        if self._arch is not None:
            cname += f"-{self._arch}"

        if self._commit_id is not None:
            cname += f"-{self.version_and_commit_id}"

        return cname

    @property
    def commit_id(self) -> Optional[str]:
        return self._commit_id

    @property
    def flavor(self) -> str:
        return self._flavor

    @property
    def feature_set(self) -> str:
        return Parser().filter_as_string(self.flavor)

    @property
    def version(self) -> Optional[str]:
        return self._version

    @property
    def version_and_commit_id(self) -> Optional[str]:
        if self._commit_id is None:
            return None

        return f"{self._version}-{self._commit_id}"
