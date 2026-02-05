# -*- coding: utf-8 -*-

from ...apt import CopyrightFile as _CopyrightFile
from ..cname import CName


class CopyrightFile(_CopyrightFile):
    def __init__(self, feature_package_name, *args, **kwargs):
        package_name = "gardenlinux-" + CName.get_camel_case_name_for_feature(
            feature_package_name, "-"
        )

        _CopyrightFile.__init__(self, package_name, *args, **kwargs)
