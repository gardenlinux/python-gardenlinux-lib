# -*- coding: utf-8 -*-

from collections import OrderedDict
from os import PathLike
from pathlib import Path
import os

from .debian_file_mixin import DebianFileMixin


class InstallFile(DebianFileMixin):
    def __init__(self, dir_path, package_name):
        DebianFileMixin.__init__(self)

        if not isinstance(dir_path, PathLike):
            dir_path = Path(dir_path)

        self._install_definitions = OrderedDict()
        self._install_dir_path = dir_path
        self._package_name = package_name

    def add_directory(self, dir_path, target_dir):
        if not isinstance(dir_path, PathLike):
            dir_path = Path(dir_path)

        if not dir_path.is_dir():
            raise ValueError("Directory given is invalid")

        self._install_definitions[target_dir] = str(
            dir_path.joinpath("*").relative_to(self._install_dir_path)
        )

    def add_entry(self, path_name, target_path_name):
        if not isinstance(path_name, PathLike):
            path_name = Path(path_name)

        if not os.access(path_name, os.R_OK):
            raise ValueError("Install entry given is not readable")

        self._install_definitions[target_path_name] = str(
            path_name.relative_to(self._install_dir_path)
        )

    @property
    def content(self):
        content = ""

        if len(self._install_definitions) > 0:
            for target_path_name, source_path_name in self._install_definitions.items():
                content += f"{source_path_name} {target_path_name}\n"

        return content

    def generate(self, target_dir):
        self._generate(target_dir, f"{self._package_name}.install", self.content)
