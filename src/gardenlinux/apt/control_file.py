# -*- coding: utf-8 -*-

from os import PathLike
from pathlib import Path
import textwrap

from ..constants import GL_AUTHORS_EMAIL, GL_AUTHORS_NAME, GL_HOME_URL
from .debian_file_mixin import DebianFileMixin


class ControlFile(dict, DebianFileMixin):
    def __init__(self, package_name, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        DebianFileMixin.__init__(self)

        self._conflicts = []
        self._breaking_packages = []
        self._dependencies = []
        self["package_name"] = package_name
        self._packages = []

    @property
    def content(self):
        homepage = self.get("homepage", GL_HOME_URL)
        maintainer = self.get("maintainer", GL_AUTHORS_NAME)
        maintainer_email = self.get("maintainer_email", GL_AUTHORS_EMAIL)

        content = f"""
Source: {self["package_name"]}
Standards-Version: 4.0.0
Section: universe
Priority: optional
Maintainer: {maintainer} <{maintainer_email}>
Build-Depends: debhelper-compat (=12)
Homepage: {homepage}
        """.strip()

        for package in self._packages:
            content += f"\n\n{package}"

            if len(self._dependencies) > 0:
                dependencies = textwrap.indent(", ".join(self._dependencies), " ")
                content += f"\nDepends:{dependencies}"

            if len(self._conflicts) > 0:
                dependencies = textwrap.indent(", ".join(self._conflicts), " ")
                content += f"\nConflicts:{dependencies}"

            if len(self._breaking_packages) > 0:
                dependencies = textwrap.indent(", ".join(self._breaking_packages), " ")
                content += f"\nBreaks:{dependencies}"

        content += "\n"

        return content

    def add_breaking_package(self, package_name):
        if (
            package_name not in self._breaking_packages
            and package_name not in self._conflicts
        ):
            self._breaking_packages.append(package_name)

    def add_conflict(self, package_name):
        if (
            package_name not in self._breaking_packages
            and package_name not in self._conflicts
        ):
            self._conflicts.append(package_name)

    def add_dependency(self, package_name):
        if package_name not in self._dependencies:
            self._dependencies.append(package_name)

    def add_package(self, package_name, description, architecture=None):
        if architecture is None:
            architecture = "any"

        description = textwrap.indent(description.strip(), " ")

        content = f"""
Package: {package_name}
Architecture: {architecture}
Description:{description}
        """

        self._packages.append(content.strip())

    def generate(self, target_dir):
        if not isinstance(target_dir, PathLike):
            target_dir = Path(target_dir)

        if not target_dir.is_dir():
            raise ValueError("Target directory given is invalid")

        source_dir_path = target_dir.joinpath("source")
        format_file_path = source_dir_path.joinpath("format")

        if format_file_path.is_file():
            raise RuntimeError(
                "Target directory already contains a 'source/format' file"
            )

        if not source_dir_path.is_dir():
            source_dir_path.mkdir()

        self._generate(target_dir, "control", self.content)
        self._generate(source_dir_path, "format", "3.0 (native)")
