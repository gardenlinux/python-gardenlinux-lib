# -*- coding: utf-8 -*-

from ...apt import ControlFile as _ControlFile
from ..cname import CName


class ControlFile(_ControlFile):
    def __init__(self, feature_package_name, feature, *args, **kwargs):
        self._architecture = "all"
        self._feature = feature

        self._package_name = "gardenlinux-" + CName.get_camel_case_name_for_feature(
            feature_package_name, "-"
        )

        _ControlFile.__init__(self, self._package_name, *args, **kwargs)

    @_ControlFile.content.getter
    def content(self):
        self.add_package(
            self._package_name,
            f"Provides GL/features/{self._feature}",
            self._architecture,
        )
        return _ControlFile.content.fget(self)

    def add_dependency(self, package_name):
        if "${Arch}" in package_name or ("[" in  package_name and "]" in  package_name):
            self._architecture = "any"

        _ControlFile.add_dependency(self, package_name)
