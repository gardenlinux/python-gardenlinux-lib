# -*- coding: utf-8 -*-

from ...apt import InstallFile as _InstallFile
from ..cname import CName


class InstallFile(_InstallFile):
    def __init__(self, dir_path, feature_package_name):
        package_name = "gardenlinux-" + CName.get_camel_case_name_for_feature(
            feature_package_name, "-"
        )

        _InstallFile.__init__(self, dir_path, package_name)
