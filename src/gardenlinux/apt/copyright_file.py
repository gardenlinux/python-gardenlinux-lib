# -*- coding: utf-8 -*-

from collections import OrderedDict
import textwrap

from ..constants import GL_AUTHORS_EMAIL, GL_AUTHORS_NAME, GL_REPOSITORY_URL
from .debian_file_mixin import DebianFileMixin


class CopyrightFile(dict, DebianFileMixin):
    def __init__(self, package_name, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        DebianFileMixin.__init__(self)

        self["package_name"] = package_name

        self._licensed_files_entries = OrderedDict()
        self._license_text_entries = {}

    def add_licensed_files_declaration(
        self,
        files_definition_string,
        copyright_note,
        license_id=None,
        license_text=None,
    ):
        if files_definition_string in self._licensed_files_entries:
            raise ValueError(
                "A license has already been declared for the files definition given"
            )

        if license_id is None and license_text is None:
            license_id = "MIT"

            license_text = f"""
{copyright_note}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
            """

        if license_id is None or license_text is None:
            raise ValueError("Invalid input for license ID or text")

        if (
            license_id in self._license_text_entries
            and self._license_text_entries[license_id] != license_text
        ):
            raise ValueError("Given license text for already used license ID differs")

        self._license_text_entries[license_id] = license_text.strip()

        files_definition_string = textwrap.indent(files_definition_string.strip(), " ")
        copyright_note = textwrap.indent(copyright_note.strip(), " ")

        content = f"""
Files:{files_definition_string}
Copyright:{copyright_note}
License: {license_id}
        """.strip()

        self._licensed_files_entries[files_definition_string] = content

    @property
    def content(self):
        if len(self._licensed_files_entries) < 1:
            self.add_licensed_files_declaration("*", self._generate_copyright_note())

        maintainer = self.get("maintainer", GL_AUTHORS_NAME)
        maintainer_email = self.get("maintainer_email", GL_AUTHORS_EMAIL)
        package_name = self["package_name"]
        source_url = self.get("source_url", GL_REPOSITORY_URL)

        content = f"""
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Source: {source_url}
Upstream-Name: {package_name}
Upstream-Contact: {maintainer} <{maintainer_email}>
        """.strip()

        for entry in self._licensed_files_entries.values():
            content += f"\n\n{entry}"

        for entry_id, entry_text in self._license_text_entries.items():
            entry_text = textwrap.indent(entry_text, " ")
            content += f"\n\nLicense: {entry_id}\n{entry_text}"

        content += "\n"

        return content

    def generate(self, target_dir):
        self._generate(target_dir, "copyright", self.content)

    def _generate_copyright_note(self):
        return self.get("copyright", f"Copyright (c) {GL_AUTHORS_NAME}")
