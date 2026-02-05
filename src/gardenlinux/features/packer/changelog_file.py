# -*- coding: utf-8 -*-

from time import time

from ...apt import ChangelogFile as _ChangelogFile
from ..cname import CName


class ChangelogFile(_ChangelogFile):
    def __init__(
        self,
        feature_package_name,
        package_version,
        maintainer=None,
        maintainer_email=None,
    ):
        package_name = "gardenlinux-" + CName.get_camel_case_name_for_feature(
            feature_package_name, "-"
        )

        _ChangelogFile.__init__(self, package_name, maintainer, maintainer_email)

        self.add_entry(
            package_version, time(), f"* Automated build for {package_version}"
        )
