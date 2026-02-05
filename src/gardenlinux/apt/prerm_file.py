# -*- coding: utf-8 -*-

from .code_file_mixin import CodeFileMixin
from .debian_file_mixin import DebianFileMixin


class PrermFile(CodeFileMixin, DebianFileMixin):
    def __init__(
        self,
        executable="/usr/bin/env bash",
        header_code="set -euo pipefail",
        footer_code="exit 0",
    ):
        CodeFileMixin.__init__(self, executable, header_code, footer_code)
        DebianFileMixin.__init__(self)

    def generate(self, target_dir):
        self._generate(target_dir, "prerm", self.content, 0o755)
