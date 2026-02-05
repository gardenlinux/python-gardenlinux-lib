# -*- coding: utf-8 -*-

from os import PathLike
from pathlib import Path
import os

from .debian_file_mixin import DebianFileMixin


class DocsFile(DebianFileMixin):
    def __init__(self):
        DebianFileMixin.__init__(self)
        self._files = []

    def add_file(self, file_path_name):
        if not isinstance(file_path_name, PathLike):
            file_path_name = Path(file_path_name)

        if not file_path_name.is_file():
            raise ValueError("File given is invalid")

        if not os.access(file_path_name, os.R_OK):
            raise ValueError("File given is not readable")

        self._files.append(file_path_name)

    @property
    def content(self):
        content = ""

        if len(self._files) > 0:
            for file_path_name in self._files:
                content += f"{file_path_name.name}\n"

        return content

    def generate(self, debian_dir):
        target_dir = debian_dir.parent

        for file_path_name in self._files:
            self._generate(target_dir, file_path_name.name, file_path_name.read_text())

        self._generate(debian_dir, "docs", self.content)
