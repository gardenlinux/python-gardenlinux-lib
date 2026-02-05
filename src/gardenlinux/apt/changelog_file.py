# -*- coding: utf-8 -*-

from time import gmtime, strftime
import textwrap

from ..constants import GL_AUTHORS_EMAIL, GL_AUTHORS_NAME
from .debian_file_mixin import DebianFileMixin


class ChangelogFile(DebianFileMixin):
    def __init__(self, package_name, maintainer=None, maintainer_email=None):
        DebianFileMixin.__init__(self)

        self._entries = []
        self._package_name = package_name

        if maintainer is None:
            maintainer = GL_AUTHORS_NAME
        if maintainer_email is None:
            maintainer_email = GL_AUTHORS_EMAIL

        self._maintainer = maintainer
        self._maintainer_email = maintainer_email

    @property
    def content(self):
        content = ""

        for entry in self._entries:
            content += f"{entry}\n\n"

        return content.strip() + "\n"

    def add_entry(
        self,
        package_version,
        package_timestamp,
        changes,
        maintainer=None,
        maintainer_email=None,
    ):
        if maintainer is None:
            maintainer = self._maintainer
        if maintainer_email is None:
            maintainer_email = self._maintainer_email

        changes = textwrap.indent(changes.strip(), "  ")

        package_timestamp_string = strftime(
            "%a, %d %b %Y %H:%M:%S +0000", gmtime(package_timestamp)
        )

        content = f"""
{self._package_name} ({package_version}) universal; urgency=low

{changes}

 -- {maintainer} <{maintainer_email}>  {package_timestamp_string}
        """

        self._entries.append(content.strip())

    def generate(self, target_dir):
        self._generate(target_dir, "changelog", self.content)
